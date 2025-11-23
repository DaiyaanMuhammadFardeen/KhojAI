#!/usr/bin/env python3

from duckduckgo_search import DDGS

print("Testing DDGS directly...")

try:
    with DDGS() as ddgs:
        results = list(ddgs.text("Python programming", max_results=3))
        print(f"Got {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.get('title', 'No title')}: {result.get('href', 'No URL')}")
    print("SUCCESS: DDGS is working correctly!")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()