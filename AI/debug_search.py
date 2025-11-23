#!/usr/bin/env python3
"""
Debug script to trace exactly what's happening in the search_and_extract function
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from web_search import search_and_extract
    from prompt_analyzer import analyze_prompt
    
    # Test with the actual prompt
    prompt = "Tell me who is the chief advisor of bangladesh government after the July Revolution in 2024 is"
    
    print(f"Debugging search for prompt: '{prompt}'")
    print("=" * 70)
    
    # Get the search queries
    result = analyze_prompt(prompt)
    search_queries = result.get("search_queries", [])
    keyword_terms = [k['term'] for k in result.get("keywords", [])]
    
    print("Generated search queries:")
    for i, query in enumerate(search_queries, 1):
        print(f"{i}. '{query}'")
    
    print("\nKeyword terms:")
    for i, term in enumerate(keyword_terms[:5], 1):
        print(f"{i}. '{term}'")
    
    print("\nTesting search_and_extract function:")
    print("-" * 50)
    
    # Test the first query
    if search_queries:
        query = search_queries[0]
        print(f"Calling search_and_extract('{query}', {keyword_terms[:3]})")
        
        results = search_and_extract(query, keyword_terms[:3])
        print(f"Returned {len(results)} results:")
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  URL: {result.get('url', 'N/A')}")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  Relevant sentences: {len(result.get('relevant_sentences', []))}")
            for j, sentence in enumerate(result.get('relevant_sentences', [])[:3], 1):
                print(f"    {j}. {sentence[:100]}...")
    
    if not search_queries:
        print("No search queries generated!")
        
except Exception as e:
    print(f"Error during debug: {e}")
    import traceback
    traceback.print_exc()