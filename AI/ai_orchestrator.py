import time
import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from prompt_analyzer import analyze_prompt_async
from web_search import search_and_extract
import ollama  # Lightweight LLM interface

# Global LLM client for reuse
_ollama_client = None

# Simple circuit breaker implementation
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self):
        if self.state == 'OPEN':
            if (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                return True
            return False
        return True
    
    def on_success(self):
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

# Circuit breakers for external services
_ollama_circuit_breaker = CircuitBreaker()
_search_circuit_breaker = CircuitBreaker()


def get_ollama_client():
    """Get or create a global Ollama client for reuse."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = ollama.Client()
    return _ollama_client

async def generate_response_with_web_search(prompt: str) -> str:
    """
    Generate a response using web search to augment the LLM's knowledge.
    """

    # Step 1: Analyze the prompt
    print(f"Analyzing prompt: {prompt}")
    analysis = await analyze_prompt_async(prompt)

    intents = analysis.get("intents", [])
    keywords = analysis.get("keywords", [])
    search_queries = analysis.get("search_queries", [])

    print(f"Identified intents: {intents}")
    print(f"Extracted keywords: {[k['term'] for k in keywords]}")
    print(f"Generated search queries: {search_queries}")

    search_intents = ["web_search", "question", "explanation", "research", "question_answering", "planning"]
    needs_search = any(intent in search_intents for intent in intents)

    unique_information = []

    # Step 2: Perform search if needed
    if needs_search and search_queries:
        # Check circuit breaker for search
        if not _search_circuit_breaker.can_execute():
            print("Circuit breaker is OPEN for search, skipping web search")
            return "I'm sorry, but I'm having trouble accessing web search right now. Please try again later."

        all_information = []
        keyword_terms = [k['term'] for k in keywords]

        try:
            for query in search_queries[:3]:
                print(f"Searching web for: {query}")
                information = await search_and_extract(query, keyword_terms)
                all_information.extend(information)
                await asyncio.sleep(0.5)
            
            _search_circuit_breaker.on_success()
        except Exception as e:
            print(f"Error during web search: {e}")
            _search_circuit_breaker.on_failure()
            return "I'm sorry, but I'm having trouble accessing web search right now. Please try again later."

        seen_urls = set()
        for info in all_information:
            if info["url"] not in seen_urls:
                seen_urls.add(info["url"])
                unique_information.append(info)

        print(f"Found information from {len(unique_information)} sources")

    elif needs_search and not search_queries:
        # Check circuit breaker for search
        if not _search_circuit_breaker.can_execute():
            print("Circuit breaker is OPEN for search, skipping web search")
            return "I'm sorry, but I'm having trouble accessing web search right now. Please try again later."

        print(f"Performing general web search for: {prompt}")
        try:
            information = await search_and_extract(prompt, [prompt])
            unique_information.extend(information)
            _search_circuit_breaker.on_success()
            print(f"Found information from {len(unique_information)} sources")
        except Exception as e:
            print(f"Error during web search: {e}")
            _search_circuit_breaker.on_failure()
            return "I'm sorry, but I'm having trouble accessing web search right now. Please try again later."

    else:
        print(f"Skipping web search for intents: {intents}")

    # Step 3: Generate response
    if unique_information:
        context = build_context_from_information(unique_information)
        response = generate_coherent_response(prompt, context)
        return response
    else:
        return "I'm sorry, but I couldn't find relevant information to answer your query."


async def generate_response_with_web_search_stream(prompt: str, raw_stream: bool = False) -> AsyncGenerator[str, None]:
    """
    Generate a streamed response using web search.
    """

    if not raw_stream:
        yield f"data: {json.dumps({'type': 'prompt_analysis', 'status': 'started'})}\n\n"
    
    print(f"Analyzing prompt: {prompt}")
    analysis = await analyze_prompt_async(prompt)
    
    intents = analysis.get("intents", [])
    keywords = analysis.get("keywords", [])
    search_queries = analysis.get("search_queries", [])
    
    if not raw_stream:
        yield f"data: {json.dumps({'type': 'prompt_analysis', 'status': 'completed', 'intents': intents, 'keywords': keywords, 'search_queries': search_queries})}\n\n"
    else:
        # For terminal app, send analysis info directly
        yield f"[ANALYSIS] Intents: {intents}\n"
        yield f"[ANALYSIS] Keywords: {[k['term'] for k in keywords]}\n"
        yield f"[ANALYSIS] Search Queries: {search_queries}\n\n"

    print(f"Identified intents: {intents}")
    print(f"Extracted keywords: {[k['term'] for k in keywords]}")
    print(f"Generated search queries: {search_queries}")

    search_intents = ["web_search", "question", "explanation", "research", "question_answering"]
    needs_search = any(intent in search_intents for intent in intents)

    unique_information = []

    if needs_search and search_queries:
        if not raw_stream:
            yield f"data: {json.dumps({'type': 'web_search', 'status': 'started'})}\n\n"
        else:
            yield f"[SEARCH] Starting web search...\n"
            
        # Check circuit breaker for search
        if not _search_circuit_breaker.can_execute():
            print("Circuit breaker is OPEN for search, skipping web search")
            if not raw_stream:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Web search is temporarily unavailable'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            else:
                yield f"[ERROR] Web search is temporarily unavailable\n"
            return

        all_information = []
        keyword_terms = [k['term'] for k in keywords]

        try:
            for i, query in enumerate(search_queries[:3]):
                if not raw_stream:
                    yield f"data: {json.dumps({'type': 'web_search', 'status': 'progress', 'query': query, 'current': i+1, 'total': min(len(search_queries), 3)})}\n\n"
                else:
                    yield f"[SEARCH] Query {i+1}/{min(len(search_queries), 3)}: {query}\n"
                print(f"Searching web for: {query}")
                information = await search_and_extract(query, keyword_terms)
                all_information.extend(information)
                await asyncio.sleep(0.5)
            
            _search_circuit_breaker.on_success()
        except Exception as e:
            print(f"Error during web search: {e}")
            _search_circuit_breaker.on_failure()
            if not raw_stream:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Web search is temporarily unavailable'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            else:
                yield f"[ERROR] Web search is temporarily unavailable\n"
            return

        seen_urls = set()
        search_results = []
        for info in all_information:
            if info["url"] not in seen_urls:
                seen_urls.add(info["url"])
                unique_information.append(info)
                search_results.append({
                    "title": info.get("title", "Untitled"),
                    "url": info["url"]
                })

        print(f"Found information from {len(unique_information)} sources")
        if not raw_stream:
            yield f"data: {json.dumps({'type': 'web_search', 'status': 'completed', 'sources': len(unique_information)})}\n\n"
        else:
            yield f"[SEARCH] Found information from {len(unique_information)} sources\n"
            # Provide details about search results
            for result in search_results[:5]:  # Limit to first 5 results
                yield f"[SEARCH] Result: {result['title']} - {result['url']}\n"
            yield "\n"

    elif needs_search and not search_queries:
        # Check circuit breaker for search
        if not raw_stream:
            yield f"data: {json.dumps({'type': 'web_search', 'status': 'started'})}\n\n"
        else:
            yield f"[SEARCH] Starting general web search...\n"
            
        if not _search_circuit_breaker.can_execute():
            print("Circuit breaker is OPEN for search, skipping web search")
            if not raw_stream:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Web search is temporarily unavailable'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            else:
                yield f"[ERROR] Web search is temporarily unavailable\n"
            return

        print(f"Performing general web search for: {prompt}")
        try:
            information = await search_and_extract(prompt, [prompt])
            unique_information.extend(information)
            _search_circuit_breaker.on_success()
            print(f"Found information from {len(unique_information)} sources")
            if not raw_stream:
                yield f"data: {json.dumps({'type': 'web_search', 'status': 'completed', 'sources': len(unique_information)})}\n\n"
            else:
                yield f"[SEARCH] Found information from {len(unique_information)} sources\n"
                # Provide details about search results
                search_results = []
                for info in unique_information[:5]:  # Limit to first 5 results
                    search_results.append({
                        "title": info.get("title", "Untitled"),
                        "url": info["url"]
                    })
                for result in search_results:
                    yield f"[SEARCH] Result: {result['title']} - {result['url']}\n"
                yield "\n"
        except Exception as e:
            print(f"Error during web search: {e}")
            _search_circuit_breaker.on_failure()
            if not raw_stream:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Web search is temporarily unavailable'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            else:
                yield f"[ERROR] Web search is temporarily unavailable\n"
            return

    else:
        print(f"Skipping web search for intents: {intents}")
        if not raw_stream:
            yield f"data: {json.dumps({'type': 'web_search', 'status': 'skipped', 'reason': f'Skipping web search for intents: {intents}'})}\n\n"
        else:
            yield f"[SEARCH] Skipped web search for intents: {intents}\n\n"

    # Step 3: Stream response
    if unique_information:
        context = build_context_from_information(unique_information)
        if not raw_stream:
            yield f"data: {json.dumps({'type': 'response_generation', 'status': 'started'})}\n\n"
        else:
            yield f"[RESPONSE] Generating coherent response...\n\n"
            
        # Stream the response token by token
        for token in generate_coherent_response_stream(prompt, context):
            if not raw_stream:
                yield f"data: {json.dumps({'type': 'response_token', 'token': token})}\n\n"
            else:
                yield token
        
        if not raw_stream:
            yield f"data: {json.dumps({'type': 'response_generation', 'status': 'completed'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        else:
            yield "\n[RESPONSE] Completed.\n"
        return

    # Web search not required OR returned nothing
    if not raw_stream:
        yield f"data: {json.dumps({'type': 'response_generation', 'status': 'started'})}\n\n"
    else:
        yield f"[RESPONSE] Generating fallback response...\n\n"

    # Stream fallback response token by token
    for token in generate_fallback_response_stream(prompt.strip()):
        if not raw_stream:
            yield f"data: {json.dumps({'type': 'response_token', 'token': token})}\n\n"
        else:
            yield token
    
    if not raw_stream:
        yield f"data: {json.dumps({'type': 'response_generation', 'status': 'completed'})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    else:
        yield "\n[RESPONSE] Completed.\n"


def build_context_from_information(information: List[Dict[str, Any]]) -> str:
    context_parts = []

    for info in information:
        source_info = f"Source: {info['title']} ({info['url']})"
        # Updated to handle the new format (sentence, score, metadata)
        content_info = "\n".join([sentence for sentence, _, _ in info['relevant_sentences']])
        context_parts.append(f"{source_info}\n{content_info}\n")

    return "\n---\n".join(context_parts)


def generate_coherent_response(prompt: str, context: str) -> str:
    # Check circuit breaker
    if not _ollama_circuit_breaker.can_execute():
        print("Circuit breaker is OPEN for Ollama, using fallback response")
        return f"Based on my search, here's what I found:\n\n{context}"
    
    try:
        prompt_template = f"""
Forget any information that you may have stored right now. They are all outdated.
Only the below information is up to date. You are acting as a helpful AI assistant.
The user's query is "{prompt}".

Use the context to answer. If irrelevant, reply with:
"I'm sorry, but I couldn't find relevant information to answer your query..."

Context Information:
{context}
"""
        client = get_ollama_client()
        response = client.generate(
            model="gemma3:1b",
            prompt=prompt_template,
            stream=False
        )
        _ollama_circuit_breaker.on_success()
        return response['response'].strip()

    except Exception as e:
        print(f"Error generating response with LLM: {e}")
        _ollama_circuit_breaker.on_failure()
        return f"Based on my search, here's what I found:\n\n{context}"


def generate_coherent_response_stream(prompt: str, context: str):
    """
    Generate a streamed response using the LLM with context.
    """
    # Check circuit breaker
    if not _ollama_circuit_breaker.can_execute():
        print("Circuit breaker is OPEN for Ollama, using fallback response")
        yield f"Based on my search, here's what I found:\n\n{context}"
        return
    
    try:
        prompt_template = f"""
Forget any information that you may have stored right now. They are all outdated.
Only the below information is up to date. You are acting as a helpful AI assistant.
The user's query is "{prompt}".

Use the context to answer. If irrelevant, reply with:
"I'm sorry, but I couldn't find relevant information to answer your query..."

Context Information:
{context}
"""
        client = get_ollama_client()
        response_stream = client.generate(
            model="gemma3:1b",
            prompt=prompt_template,
            stream=True
        )
        
        for chunk in response_stream:
            if 'response' in chunk:
                yield chunk['response']
        
        _ollama_circuit_breaker.on_success()
        
    except Exception as e:
        print(f"Error generating response with LLM: {e}")
        _ollama_circuit_breaker.on_failure()
        yield f"Based on my search, here's what I found:\n\n{context}"


def generate_fallback_response(prompt: str) -> str:
    # Check circuit breaker
    if not _ollama_circuit_breaker.can_execute():
        print("Circuit breaker is OPEN for Ollama, using simple fallback response")
        return "I'm here to help! What would you like to know?"
    
    try:
        client = get_ollama_client()
        response = client.generate(
            model="gemma3:1b",
            prompt=f"You are a helpful AI assistant. Answer: {prompt}",
            stream=False
        )
        _ollama_circuit_breaker.on_success()
        return response['response'].strip()
    except Exception as e:
        print(f"Error generating fallback response: {e}")
        _ollama_circuit_breaker.on_failure()
        return "I'm here to help! What would you like to know?"


def generate_fallback_response_stream(prompt: str):
    """
    Generate a streamed fallback response using the LLM.
    """
    # Check circuit breaker
    if not _ollama_circuit_breaker.can_execute():
        print("Circuit breaker is OPEN for Ollama, using simple fallback response")
        yield "I'm here to help! What would you like to know?"
        return
    
    try:
        client = get_ollama_client()
        response_stream = client.generate(
            model="gemma3:1b",
            prompt=f"You are a helpful AI assistant. Answer: {prompt}",
            stream=True
        )
        
        for chunk in response_stream:
            if 'response' in chunk:
                yield chunk['response']
        
        _ollama_circuit_breaker.on_success()
        
    except Exception as e:
        print(f"Error generating fallback response: {e}")
        _ollama_circuit_breaker.on_failure()
        yield "I'm here to help! What would you like to know?"


if __name__ == "__main__":
    async def main():
        test_prompt = "Tell me everything you know about Assassin's Creed Shadows and it's latest DLC with colaboration with Attack on Titans."
        response = await generate_response_with_web_search(test_prompt)
        print("\nGenerated Response:\n", response)
    
    asyncio.run(main())