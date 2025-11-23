#!/usr/bin/env python3
"""
Test script to check if the search functionality works with improved queries
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from search_utils import search_web
    from prompt_analyzer import analyze_prompt
    
    # Test with the actual prompt
    prompt = "Tell me who is the chief advisor of bangladesh government after the July Revolution in 2024 is"
    
    print(f"Testing search for prompt: '{prompt}'")
    print("=" * 70)
    
    # Get the search queries
    result = analyze_prompt(prompt)
    search_queries = result.get("search_queries", [])
    
    print("Generated search queries:")
    for i, query in enumerate(search_queries, 1):
        print(f"{i}. '{query}'")
    
    print("\nTesting searches:")
    print("-" * 50)
    
    all_urls = []
    for i, query in enumerate(search_queries, 1):
        print(f"\nSearch {i} for '{query}':")
        urls = search_web(query, num_results=2)
        if urls:
            print(f"  Found {len(urls)} URLs:")
            for j, url in enumerate(urls, 1):
                print(f"    {j}. {url}")
                all_urls.append(url)
        else:
            print("  No URLs found")
    
    # Remove duplicates while preserving order
    unique_urls = []
    seen = set()
    for url in all_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    print(f"\nTotal unique URLs found: {len(unique_urls)}")
    for i, url in enumerate(unique_urls, 1):
        print(f"{i}. {url}")
        
    if not unique_urls:
        print("\nNo URLs found. This indicates a problem with the search functionality.")
    else:
        print(f"\nSuccess! Found {len(unique_urls)} unique sources.")
        
except Exception as e:
    print(f"Error during search: {e}")
    import traceback
    traceback.print_exc()