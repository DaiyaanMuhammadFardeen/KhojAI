"""
Example of integrating the disk-based JSON cache with the web scraping pipeline.
"""

import asyncio
from typing import Dict, List, Optional
from cache.disk_cache import DiskJsonCache
from scrape_util import scrape_webpage


async def cached_scrape_webpage(url: str, cache: Optional[DiskJsonCache] = None) -> Dict:
    """
    Scrape a webpage with caching support.
    
    Args:
        url: URL to scrape
        cache: Cache instance (optional)
        
    Returns:
        Scraped data dictionary
    """
    # If cache is provided, try to get from cache first
    if cache:
        cached_data = await cache.get(url)
        if cached_data:
            print(f"Cache hit for {url}")
            return cached_data
    
    # If not in cache or cache disabled, scrape the page
    print(f"Scraping {url}")
    scraped_data = await scrape_webpage(url)
    
    # If cache is provided, store the result
    if cache:
        await cache.set(url, scraped_data, success=scraped_data.get("fetch_success", False))
    
    return scraped_data


async def search_cached_content(query: str, cache: DiskJsonCache, limit: int = 10) -> List[Dict]:
    """
    Search cached content using full-text search.
    
    Args:
        query: Search query
        cache: Cache instance
        limit: Maximum number of results
        
    Returns:
        List of matching documents
    """
    print(f"Searching cache for: {query}")
    results = await cache.search(query, limit)
    print(f"Found {len(results)} cached documents matching '{query}'")
    return results


async def example_usage():
    """Example usage of the caching system."""
    # Initialize cache
    cache = DiskJsonCache("cache")
    
    # Example URLs to scrape
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/xml"
    ]
    
    # Scrape with caching
    print("=== Scraping with Caching ===")
    for url in urls:
        data = await cached_scrape_webpage(url, cache)
        print(f"Title: {data.get('title', 'N/A')}")
        print(f"Content length: {len(data.get('content', ''))}")
        print("-" * 40)
    
    # Show cache stats
    stats = cache.stats()
    print(f"\nCache Stats: {stats['total_items']} items, {stats['total_size']} bytes")
    
    # Search cached content
    print("\n=== Searching Cached Content ===")
    search_results = await search_cached_content("example", cache, limit=5)
    for result in search_results:
        print(f"Found: {result.get('title', 'N/A')} ({result.get('url', 'N/A')})")


if __name__ == "__main__":
    asyncio.run(example_usage())