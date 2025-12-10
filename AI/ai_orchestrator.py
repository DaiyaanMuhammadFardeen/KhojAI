import time
import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from prompt_analyzer import analyze_prompt_async
from web_search import search_and_extract
from unified_stream import StreamEvent, EVENT_TYPES
import ollama  # Lightweight LLM interface
from datetime import datetime
today_date = datetime.now().strftime("%Y-%m-%d")

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
    context = build_context_from_information(unique_information)
    response = generate_coherent_response(prompt, context)
    return response


async def generate_unified_stream(prompt: str) -> AsyncGenerator[str, None]:
    """
    Generate a unified stream combining intent analysis, search, and response generation.
    """

    # Emit intent detection start event
    event = StreamEvent(EVENT_TYPES["INTENT_DETECTED"], {"status": "started"})
    yield f"data: {event.to_json()}\n\n"
    
    print(f"Analyzing prompt: {prompt}")
    analysis = await analyze_prompt_async(prompt)
    
    intents = analysis.get("intents", [])
    keywords = analysis.get("keywords", [])
    search_queries = analysis.get("search_queries", [])
    
    # Emit intent detection completion event
    event = StreamEvent(EVENT_TYPES["INTENT_DETECTED"], {
        "status": "completed", 
        "intents": intents, 
        "keywords": keywords, 
        "search_queries": search_queries
    })
    yield f"data: {event.to_json()}\n\n"

    print(f"Identified intents: {intents}")
    print(f"Extracted keywords: {[k['term'] for k in keywords]}")
    print(f"Generated search queries: {search_queries}")

    search_intents = ["web_search", "question", "explanation", "research", "question_answering"]
    needs_search = any(intent in search_intents for intent in intents)

    unique_information = []

    if needs_search and search_queries:
        # Emit search start event
        event = StreamEvent(EVENT_TYPES["SEARCH_STARTED"], {"status": "started"})
        yield f"data: {event.to_json()}\n\n"
            
        # Check circuit breaker for search
        if not _search_circuit_breaker.can_execute():
            print("Circuit breaker is OPEN for search, skipping web search")
            event = StreamEvent(EVENT_TYPES["PROCESSING_ERROR"], {"message": "Web search is temporarily unavailable"})
            yield f"data: {event.to_json()}\n\n"
            
            event = StreamEvent(EVENT_TYPES["STREAM_COMPLETE"], {})
            yield f"data: {event.to_json()}\n\n"
            return

        all_information = []
        keyword_terms = [k['term'] for k in keywords]

        try:
            for i, query in enumerate(search_queries[:3]):
                # Emit search progress event
                event = StreamEvent(EVENT_TYPES["SEARCH_PROGRESS"], {
                    "query": query, 
                    "current": i+1, 
                    "total": min(len(search_queries), 3)
                })
                yield f"data: {event.to_json()}\n\n"
                
                print(f"Searching web for: {query}")
                information = await search_and_extract(query, keyword_terms)
                all_information.extend(information)
                await asyncio.sleep(0.5)
            
            _search_circuit_breaker.on_success()
        except Exception as e:
            print(f"Error during web search: {e}")
            _search_circuit_breaker.on_failure()
            event = StreamEvent(EVENT_TYPES["PROCESSING_ERROR"], {"message": "Web search is temporarily unavailable"})
            yield f"data: {event.to_json()}\n\n"
            
            event = StreamEvent(EVENT_TYPES["STREAM_COMPLETE"], {})
            yield f"data: {event.to_json()}\n\n"
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
        # Emit search completion event with results
        event = StreamEvent(EVENT_TYPES["SEARCH_COMPLETED"], {"sources": len(unique_information)})
        yield f"data: {event.to_json()}\n\n"
        
        # Emit individual search results
        for result in search_results[:5]:  # Limit to first 5 results
            event = StreamEvent(EVENT_TYPES["SEARCH_RESULT"], {
                "title": result['title'],
                "url": result['url']
            })
            yield f"data: {event.to_json()}\n\n"

    elif needs_search and not search_queries:
        # Emit search start event
        event = StreamEvent(EVENT_TYPES["SEARCH_STARTED"], {"status": "started"})
        yield f"data: {event.to_json()}\n\n"
            
        if not _search_circuit_breaker.can_execute():
            print("Circuit breaker is OPEN for search, skipping web search")
            event = StreamEvent(EVENT_TYPES["PROCESSING_ERROR"], {"message": "Web search is temporarily unavailable"})
            yield f"data: {event.to_json()}\n\n"
            
            event = StreamEvent(EVENT_TYPES["STREAM_COMPLETE"], {})
            yield f"data: {event.to_json()}\n\n"
            return

        print(f"Performing general web search for: {prompt}")
        try:
            information = await search_and_extract(prompt, [prompt])
            unique_information.extend(information)
            _search_circuit_breaker.on_success()
            print(f"Found information from {len(unique_information)} sources")
            
            # Emit search completion event
            event = StreamEvent(EVENT_TYPES["SEARCH_COMPLETED"], {"sources": len(unique_information)})
            yield f"data: {event.to_json()}\n\n"
            
            # Emit individual search results
            search_results = []
            for info in unique_information[:5]:  # Limit to first 5 results
                search_results.append({
                    "title": info.get("title", "Untitled"),
                    "url": info["url"]
                })
                
            for result in search_results:
                event = StreamEvent(EVENT_TYPES["SEARCH_RESULT"], {
                    "title": result['title'],
                    "url": result['url']
                })
                yield f"data: {event.to_json()}\n\n"
        except Exception as e:
            print(f"Error during web search: {e}")
            _search_circuit_breaker.on_failure()
            event = StreamEvent(EVENT_TYPES["PROCESSING_ERROR"], {"message": "Web search is temporarily unavailable"})
            yield f"data: {event.to_json()}\n\n"
            
            event = StreamEvent(EVENT_TYPES["STREAM_COMPLETE"], {})
            yield f"data: {event.to_json()}\n\n"
            return

    else:
        print(f"Skipping web search for intents: {intents}")
        # Emit search skipped event
        event = StreamEvent(EVENT_TYPES["SEARCH_COMPLETED"], {
            "status": "skipped", 
            "reason": f"Skipping web search for intents: {intents}"
        })
        yield f"data: {event.to_json()}\n\n"

    # Step 3: Stream response
    # if unique_information:
        context = build_context_from_information(unique_information)
        # Emit response generation start event
        event = StreamEvent(EVENT_TYPES["RESPONSE_STARTED"], {"status": "started"})
        yield f"data: {event.to_json()}\n\n"

        # Stream the response token by token
        for token in generate_coherent_response_stream(prompt, context):
            event = StreamEvent(EVENT_TYPES["RESPONSE_TOKEN"], {"token": token})
            yield f"data: {event.to_json()}\n\n"

        # Emit response generation completion event
        event = StreamEvent(EVENT_TYPES["RESPONSE_COMPLETED"], {"status": "completed"})
        yield f"data: {event.to_json()}\n\n"

        # Emit stream completion event
        event = StreamEvent(EVENT_TYPES["STREAM_COMPLETE"], {})
        yield f"data: {event.to_json()}\n\n"
        return

    # Web search not required OR returned nothing
    # Emit response generation start event
    event = StreamEvent(EVENT_TYPES["RESPONSE_STARTED"], {"status": "started"})
    yield f"data: {event.to_json()}\n\n"

    # Stream fallback response token by token
    for token in generate_fallback_response_stream(prompt.strip()):
        event = StreamEvent(EVENT_TYPES["RESPONSE_TOKEN"], {"token": token})
        yield f"data: {event.to_json()}\n\n"
    
    # Emit response generation completion event
    event = StreamEvent(EVENT_TYPES["RESPONSE_COMPLETED"], {"status": "completed"})
    yield f"data: {event.to_json()}\n\n"
    
    # Emit stream completion event
    event = StreamEvent(EVENT_TYPES["STREAM_COMPLETE"], {})
    yield f"data: {event.to_json()}\n\n"


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
You are KhojAI — a truthful, source-grounded AI search assistant running locally. 
Your core directive is: **Never invent facts. Never guess. Never hallucinate.** 
If something is not explicitly written in the "Retrieved Context" section below, you do **not** know it and must say so.

### STRICT RULES — YOU WILL LOSE POINTS IF YOU BREAK ANY OF THESE:
1. You **must** base your entire answer only on the "Retrieved Context" provided below.
2. You **must not** add any information that is not present in the Retrieved Context.
3. You **must not** use any prior knowledge, training data, or memory — only the context given in this message is valid.
4. If the context does not contain enough information to answer the question fully, you **must** say exactly:  
   "I'm sorry, but the retrieved web sources do not contain enough information to fully answer your question."
5. If the context is completely irrelevant or empty, reply only with:  
   "I'm sorry, but I couldn't find relevant information to answer your query."
6. Do **not** make up dates, names, numbers, statistics, quotes, or events that are not verbatim in the context.
7. Do **not** continue or speculate beyond what is explicitly written.
8. You are allowed to rephrase and summarize, but every factual claim must be traceable to a sentence in the context.
9. Always prefer being concise and admitting ignorance over guessing.
10. Never apologize for following these rules — they are mandatory for correctness.

### FORMATTING REQUIREMENTS:
- Write naturally and conversationally.
- Use markdown for clarity (bullet points, bold, tables when helpful).
- At the end of your answer, add a "Sources" section listing the URLs or titles from the context that you actually used.
- If you used no sources (because nothing was relevant), write: "Sources: None — no reliable information found."

### TIME CONTEXT:
All the context are of today's time which is {today_date}
### USER QUESTION:
{prompt}

### RETRIEVED CONTEXT (this is the only truth you have):
{context}

Now think step-by-step before answering:
1. Read the user question carefully.
2. Scan the entire Retrieved Context.
3. Identify sentences that directly relate to the question.
4. If no sentence provides a clear, direct answer → use the exact "not enough information" response.
5. If yes → synthesize a concise, natural answer using only those sentences.
6. End with the Sources list.

Begin your response now."""
        client = get_ollama_client()
        response = client.generate(
            model="gemma3:4b",
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
You are KhojAI — a truthful, source-grounded AI search assistant running locally. 
Your core directive is: **Never invent facts. Never guess. Never hallucinate.** 
If something is not explicitly written in the "Retrieved Context" section below, you do **not** know it and must say so.

### STRICT RULES — YOU WILL LOSE POINTS IF YOU BREAK ANY OF THESE:
1. You **must** base your entire answer only on the "Retrieved Context" provided below.
2. You **must not** add any information that is not present in the Retrieved Context.
3. You **must not** use any prior knowledge, training data, or memory — only the context given in this message is valid.
4. If the context does not contain enough information to answer the question fully, you **must** say exactly:  
   "I'm sorry, but the retrieved web sources do not contain enough information to fully answer your question."
5. If the context is completely irrelevant or empty, reply only with:  
   "I'm sorry, but I couldn't find relevant information to answer your query."
6. Do **not** make up dates, names, numbers, statistics, quotes, or events that are not verbatim in the context.
7. Do **not** continue or speculate beyond what is explicitly written.
8. You are allowed to rephrase and summarize, but every factual claim must be traceable to a sentence in the context.
9. Always prefer being concise and admitting ignorance over guessing.
10. Never apologize for following these rules — they are mandatory for correctness.

### FORMATTING REQUIREMENTS:
- Write naturally and conversationally.
- Use markdown for clarity (bullet points, bold, tables when helpful).
- At the end of your answer, add a "Sources" section listing the URLs or titles from the context that you actually used.
- If you used no sources (because nothing was relevant), write: "Sources: None — no reliable information found."

### TIME CONTEXT:
All the context are of today's time which is {today_date}
### USER QUESTION:
{prompt}

### RETRIEVED CONTEXT (this is the only truth you have):
{context}

Now think step-by-step before answering:
1. Read the user question carefully.
2. Scan the entire Retrieved Context.
3. Identify sentences that directly relate to the question.
4. If no sentence provides a clear, direct answer → use the exact "not enough information" response.
5. If yes → synthesize a concise, natural answer using only those sentences.
6. End with the Sources list.

Begin your response now."""
        client = get_ollama_client()
        response_stream = client.generate(
            model="gemma3:4b",
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
            model="gemma3:4b",
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
            model="gemma3:4b",
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
