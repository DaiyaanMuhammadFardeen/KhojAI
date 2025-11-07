import time
from typing import List, Dict, Any
from prompt_analyzer import analyze_prompt
from web_search import search_and_extract
import ollama  # Lightweight LLM interface

def generate_response_with_web_search(prompt: str) -> str:
    """
    Generate a response using web search to augment the LLM's knowledge.
    
    Process:
    1. Analyze the prompt to extract intents and keywords
    2. Generate search queries based on the analysis
    3. Perform web searches and extract relevant information
    4. Use an LLM to generate a coherent response based on the extracted information
    """
    
    # Step 1: Analyze the prompt
    print(f"Analyzing prompt: {prompt}")
    analysis = analyze_prompt(prompt)
    
    intents = analysis.get("intents", [])
    keywords = analysis.get("keywords", [])
    search_queries = analysis.get("search_queries", [])
    
    print(f"Identified intents: {intents}")
    print(f"Extracted keywords: {[k['term'] for k in keywords]}")
    print(f"Generated search queries: {search_queries}")
    
    # Step 2: Collect information from web searches
    all_information = []
    keyword_terms = [k['term'] for k in keywords]
    
    for query in search_queries[:3]:  # Limit to top 3 search queries
        print(f"Searching web for: {query}")
        information = search_and_extract(query, keyword_terms)
        all_information.extend(information)
        
        # Small delay to be respectful to servers
        time.sleep(0.5)
    
    # Remove duplicates based on URL
    unique_information = []
    seen_urls = set()
    for info in all_information:
        if info["url"] not in seen_urls:
            seen_urls.add(info["url"])
            unique_information.append(info)
    
    print(f"Found information from {len(unique_information)} sources")
    
    # Step 3: If we found relevant information, use it to generate a response
    if unique_information:
        # Build context for the LLM
        context = build_context_from_information(unique_information)
        
        # Generate response using LLM
        response = generate_coherent_response(prompt, context)
        return response
    else:
        # Fallback: Use a general LLM response
        return generate_fallback_response(prompt)

def build_context_from_information(information: List[Dict[str, Any]]) -> str:
    """
    Build a context string from the extracted information.
    """
    context_parts = []
    
    for info in information:
        source_info = f"Source: {info['title']} ({info['url']})"
        content_info = "\n".join(info['relevant_sentences'])
        context_parts.append(f"{source_info}\n{content_info}\n")
    
    return "\n---\n".join(context_parts)

def generate_coherent_response(prompt: str, context: str) -> str:
    """
    Use a lightweight LLM to generate a coherent response based on the context.
    """
    try:
        # For lightweight models that can run on 8GB VRAM
        # This is a simplified example - you would adjust based on your specific model
        prompt_template = f"""
        You are a helpful AI assistant. Answer the user's query using the provided context.
        Be concise but comprehensive, and always cite your sources when possible.
        
        User Query: {prompt}
        
        Context Information:
        {context}
        
        Please provide a well-structured response:
        """
        
        # Using ollama as an example - replace with your preferred lightweight LLM
        response = ollama.generate(
            model="llama2",  # or another lightweight model like "mistral"
            prompt=prompt_template,
            stream=False
        )
        
        return response['response'].strip()
    except Exception as e:
        print(f"Error generating response with LLM: {e}")
        # Fallback to context-only response
        return f"Based on my search, here's what I found:\n\n{context}"

def generate_fallback_response(prompt: str) -> str:
    """
    Generate a fallback response when web search doesn't yield results.
    """
    try:
        response = ollama.generate(
            model="llama2",
            prompt=f"Please answer the following query to the best of your ability: {prompt}",
            stream=False
        )
        return response['response'].strip()
    except Exception as e:
        print(f"Error generating fallback response: {e}")
        return "I'm sorry, but I couldn't find relevant information to answer your query."

# Example usage
if __name__ == "__main__":
    # Test the orchestrator
    test_prompt = "What are the latest developments in quantum computing?"
    response = generate_response_with_web_search(test_prompt)
    print("\nGenerated Response:")
    print(response)