#!/usr/bin/env python3
"""
Test script to verify cache integration with web search functionality.
"""

import asyncio
import os
from web_search import search_and_extract, cache

async def test_cache_integration():
    """Test the cache integration by performing searches and checking cache behavior."""
    
    # Test query
    query = "Python programming language history"
    keywords = ["Python", "programming", "history", "Guido", "development"]
    
    print("=== Testing Cache Integration ===\n")
    
    # Show initial cache stats
    stats = cache.stats()
    print(f"Initial cache stats: {stats['total_items']} items\n")
    
    # First search - should populate cache
    print("--- First Search (should populate cache) ---")
    results1 = await search_and_extract(query, keywords)
    print(f"First search returned {len(results1)} results\n")
    
    # Show cache stats after first search
    stats = cache.stats()
    print(f"Cache stats after first search: {stats['total_items']} items\n")
    
    # Second search - should use cache
    print("--- Second Search (should use cache) ---")
    results2 = await search_and_extract(query, keywords)
    print(f"Second search returned {len(results2)} results\n")
    
    # Verify we got the same results
    if len(results1) == len(results2):
        print("✓ Both searches returned the same number of results")
    else:
        print("⚠ Searches returned different number of results")
    
    # Show final cache stats
    stats = cache.stats()
    print(f"\nFinal cache stats: {stats['total_items']} items")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_cache_integration())