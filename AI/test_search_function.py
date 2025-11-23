#!/usr/bin/env python3
"""
Test script to check if the search functionality is working
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from search_utils import search_web
    
    # Test with a simple query
    test_query = "Bangladesh chief advisor July 2024"
    
    print(f"Testing search for: '{test_query}'")
    print("=" * 50)
    
    urls = search_web(test_query, num_results=3)
    
    print(f"Found {len(urls)} URLs:")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")
        
    if not urls:
        print("No URLs found. This indicates a problem with the search functionality.")
        print("Possible issues:")
        print("1. DuckDuckGo search might be blocked or rate-limited")
        print("2. The ddgs library might not be working properly")
        print("3. Network connectivity issues")
        
except Exception as e:
    print(f"Error during search: {e}")
    import traceback
    traceback.print_exc()