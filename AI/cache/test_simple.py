#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from cache.disk_cache import DiskJsonCache

async def main():
    print("Testing disk-based JSON cache system...")
    
    # Initialize cache
    cache = DiskJsonCache("./test_cache")
    print("✓ Cache initialized")
    
    # Test stats
    stats = cache.stats()
    print(f"✓ Initial stats: {stats}")
    
    # Test set operation
    test_data = {
        "url": "https://example.com/test",
        "title": "Test Page",
        "content": "This is a test page content for caching system",
        "metadata": {
            "author": "Test Author",
            "tags": ["test", "cache"]
        },
        "fetch_success": True
    }
    
    await cache.set("https://example.com/test", test_data)
    print("✓ Data set in cache")
    
    # Test get operation
    retrieved = await cache.get("https://example.com/test")
    if retrieved and retrieved["title"] == "Test Page":
        print("✓ Data retrieved from cache successfully")
    else:
        print("✗ Failed to retrieve data from cache")
        return 1
    
    # Test stats again
    stats = cache.stats()
    print(f"✓ Updated stats: {stats}")
    
    print("All tests passed!")
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)