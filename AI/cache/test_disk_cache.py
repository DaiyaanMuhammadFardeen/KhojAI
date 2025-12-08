"""
Tests for the disk-based JSON cache system.
"""

import os
import sys
import tempfile
import asyncio
import pytest
from pathlib import Path

# Add the parent directory to sys.path to enable importing cache modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cache.disk_cache import DiskJsonCache


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def cache(temp_cache_dir):
    """Create a cache instance for testing."""
    return DiskJsonCache(temp_cache_dir)


def test_initialization(temp_cache_dir):
    """Test cache initialization."""
    cache = DiskJsonCache(temp_cache_dir)

    # Check that directories are created
    assert Path(temp_cache_dir).exists()
    assert Path(temp_cache_dir, "hot").exists()
    assert Path(temp_cache_dir, "cold").exists()
    assert Path(temp_cache_dir, "bm25_index").exists()

    # Check that metadata file exists
    assert Path(temp_cache_dir, "metadata.json").exists()


def test_normalize_url():
    """Test URL normalization."""
    cache = DiskJsonCache()

    # Test basic normalization
    assert cache._normalize_url("https://example.com") == "https://example.com/"
    assert cache._normalize_url("https://EXAMPLE.COM/") == "https://example.com/"
    assert cache._normalize_url("https://example.com/path") == "https://example.com/path"
    assert cache._normalize_url("https://example.com/path/") == "https://example.com/path"

    # Test query parameter sorting
    url1 = cache._normalize_url("https://example.com?a=1&b=2")
    url2 = cache._normalize_url("https://example.com?b=2&a=1")
    assert url1 == url2


def test_compute_hash():
    """Test hash computation."""
    cache = DiskJsonCache()

    # Same input should produce same hash
    hash1 = cache._compute_hash("test content")
    hash2 = cache._compute_hash("test content")
    assert hash1 == hash2

    # Different inputs should produce different hashes
    hash3 = cache._compute_hash("different content")
    assert hash1 != hash3


@pytest.mark.asyncio
async def test_set_and_get(cache):
    """Test setting and getting cache entries."""
    url = "https://example.com/test"
    data = {
        "url": url,
        "title": "Test Page",
        "content": "This is test content",
        "metadata": {
            "author": "Test Author"
        }
    }

    # Set data in cache
    await cache.set(url, data, success=True)

    # Retrieve data from cache
    retrieved = await cache.get(url)

    # Check that data matches
    assert retrieved is not None
    assert retrieved["url"] == url
    assert retrieved["title"] == "Test Page"
    assert retrieved["content"] == "This is test content"
    assert retrieved["metadata"]["author"] == "Test Author"


@pytest.mark.asyncio
async def test_deduplication(cache):
    """Test content deduplication."""
    url1 = "https://example.com/page1"
    url2 = "https://example.com/page2"
    content = "Identical content for both pages"

    data1 = {
        "url": url1,
        "title": "Page 1",
        "content": content,
        "metadata": {}
    }

    data2 = {
        "url": url2,
        "title": "Page 2",
        "content": content,  # Same content
        "metadata": {}
    }

    # Set both entries
    await cache.set(url1, data1)
    await cache.set(url2, data2)

    # Both URLs should return the same content
    retrieved1 = await cache.get(url1)
    retrieved2 = await cache.get(url2)

    assert retrieved1 is not None
    assert retrieved2 is not None
    assert retrieved1["content"] == retrieved2["content"]

    # But they should have different URLs
    assert retrieved1["url"] == url1
    assert retrieved2["url"] == url2


@pytest.mark.asyncio
async def test_expiration(cache):
    """Test cache expiration."""
    url = "https://example.com/temp"
    data = {
        "url": url,
        "title": "Temporary Page",
        "content": "This will expire quickly",
        "metadata": {}
    }

    # Set with short expiration (simulating error cache)
    cache.ERROR_CACHE_DURATION = 0  # Expire immediately
    await cache.set(url, data, success=False)

    # Should not be retrievable (expired)
    retrieved = await cache.get(url)
    assert retrieved is None


@pytest.mark.asyncio
async def test_search(cache):
    """Test full-text search functionality."""
    # Add some test data
    data1 = {
        "url": "https://example.com/news1",
        "title": "Python Programming News",
        "content": "Python is a great programming language for web development",
        "metadata": {}
    }

    data2 = {
        "url": "https://example.com/news2",
        "title": "JavaScript Frameworks",
        "content": "JavaScript is popular for frontend web development",
        "metadata": {}
    }

    await cache.set("https://example.com/news1", data1)
    await cache.set("https://example.com/news2", data2)

    # Search for Python related content
    results = await cache.search("Python programming", limit=5)

    # Should find at least one result
    assert len(results) >= 1

    # First result should contain Python
    assert "Python" in results[0]["content"] or "Python" in results[0]["title"]


@pytest.mark.asyncio
async def test_invalidate(cache):
    """Test manual cache invalidation."""
    url = "https://example.com/to_be_invalidated"
    data = {
        "url": url,
        "title": "To Be Invalidated",
        "content": "This should be removed",
        "metadata": {}
    }

    # Add to cache
    await cache.set(url, data)

    # Verify it exists
    retrieved = await cache.get(url)
    assert retrieved is not None

    # Invalidate the URL
    await cache.invalidate(url)

    # Should no longer exist
    retrieved = await cache.get(url)
    assert retrieved is None


@pytest.mark.asyncio
async def test_stats(cache):
    """Test cache statistics."""
    # Initial stats
    stats = cache.stats()
    initial_items = stats["total_items"]

    # Add an item
    data = {
        "url": "https://example.com/stats_test",
        "title": "Stats Test",
        "content": "Testing statistics",
        "metadata": {}
    }
    await cache.set("https://example.com/stats_test", data)

    # Check updated stats
    stats = cache.stats()
    assert stats["total_items"] == initial_items + 1
    assert stats["total_size"] > 0


if __name__ == "__main__":
    pytest.main([__file__])