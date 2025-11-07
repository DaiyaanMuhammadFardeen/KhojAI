#!/usr/bin/env python3

import sys
import os

# Add the AI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from prompt_analyzer import analyze_prompt
from web_search import search_and_extract
from ai_orchestrator import generate_response_with_web_search

def test_prompt_analysis():
    print("=== Testing Prompt Analysis ===")
    test_prompt = "What are the latest developments in quantum computing?"
    result = analyze_prompt(test_prompt, debug=True)
    
    print("\nAnalysis Results:")
    print(f"Intents: {result['intents']}")
    print(f"Keywords: {[kw['term'] for kw in result['keywords']]}")
    print(f"Goals: {result['goals']}")
    print(f"Search Queries: {result['search_queries']}")
    print()

def test_web_search():
    print("=== Testing Web Search ===")
    query = "quantum computing"
    keywords = ["quantum", "computing", "development"]
    
    information = search_and_extract(query, keywords)
    
    print(f"Found {len(information)} sources:")
    for i, info in enumerate(information):
        print(f"\nSource {i+1}:")
        print(f"  Title: {info['title']}")
        print(f"  URL: {info['url']}")
        print(f"  Relevant sentences: {len(info['relevant_sentences'])}")
        if info['relevant_sentences']:
            print(f"  Sample: {info['relevant_sentences'][0][:100]}...")
    print()

def test_full_pipeline():
    print("=== Testing Full Pipeline ===")
    test_prompt = "Explain the concept of quantum entanglement and its applications"
    
    print(f"Prompt: {test_prompt}")
    response = generate_response_with_web_search(test_prompt)
    print(f"Response:\n{response}")
    print()

if __name__ == "__main__":
    print("Running AI Module Tests")
    print("=" * 50)
    
    try:
        test_prompt_analysis()
    except Exception as e:
        print(f"Error in prompt analysis test: {e}")
    
    try:
        test_web_search()
    except Exception as e:
        print(f"Error in web search test: {e}")
    
    try:
        test_full_pipeline()
    except Exception as e:
        print(f"Error in full pipeline test: {e}")
    
    print("Tests completed.")