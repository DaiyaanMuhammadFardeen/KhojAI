# Disk-Based JSON Cache System

A robust, efficient caching system for web scraping pipelines that stores content as JSON files on disk with deduplication, full-text search, and hybrid hot/cold storage.

## Features

- **Minimize Redundant Scraping**: Avoid re-scraping the same content
- **Fast Lookup**: Efficient retrieval by URL and content similarity
- **Full-Text Search**: BM25-based search over cached pages
- **Automatic Deduplication**: Same content from different URLs stored once
- **Hybrid Storage**: Frequently/recently used items stay "hot" for fast access
- **Proper Expiry**: Automatic cleanup of expired entries
- **Thread-Safe**: File locking ensures data consistency
- **Zero Data Loss**: Crash-resistant writes

## Installation

```bash
pip install orjson xxhash
```

## Directory Structure

```
cache/
├── hot/                 # Small JSON files for fast access (recent + frequent)
│   └── index.json       # URL hash mapping to content hash and metadata
├── cold/                # Full archived records (one JSON file per content_hash)
│   ├── abc123...json
│   └── ...
├── bm25_index/          # For full-text search
│   └── documents.jsonl  # One line per cached document for BM25 indexing
├── metadata.json        # Global stats: total_items, total_size, last_cleanup, etc.
└── lock.file            # Simple file lock for thread/process safety
```

## Usage

### Basic Usage

```python
from cache.disk_cache import DiskJsonCache
import asyncio

# Initialize cache
cache = DiskJsonCache("cache")

# Store data
url = "https://example.com/article"
data = {
    "url": url,
    "title": "Article Title",
    "content": "Article content...",
    "metadata": {
        "author": "Author Name",
        "publish_date": "2023-01-01"
    }
}

# Store in cache
await cache.set(url, data, success=True)

# Retrieve from cache
cached_data = await cache.get(url)
```

### Full-Text Search

```python
# Search cached content
results = await cache.search("search query", limit=10)
```

### Cache Maintenance

```bash
# Run maintenance commands
python cache/maintenance.py cleanup
python cache/maintenance.py reindex-bm25
python cache/maintenance.py vacuum
python cache/maintenance.py stats
```

## Integration Example

See [example_usage.py](cache/example_usage.py) for a complete example of integrating the cache with a web scraping pipeline.

## Cache Configuration

The cache system uses the following default configuration:

```python
SUCCESS_CACHE_DURATION = 7 * 24 * 3600    # 7 days for successful scrapes
ERROR_CACHE_DURATION = 1 * 3600           # 1 hour for failed scrapes
HOT_CACHE_MAX_ITEMS = 10_000
HOT_CACHE_MAX_AGE_DAYS = 30               # Move to cold-only after 30 days
```

## Data Model

Cached entries follow this schema:

```python
{
    "url": "https://example.com/article123",           # original URL
    "canonical_url": "https://example.com/article123", # after normalization
    "final_url": "https://example.com/article123?ref=xyz", # after redirects
    "title": "Page Title",
    "content": "Extracted clean text...",
    "raw_html": "<html>...</html>",                    # optional
    "metadata": {
        "author": "John Doe",
        "publish_date": "2023-01-01",
        "tags": ["news", "tech"],
        "language": "en",
        "site_name": "Example News"
    },
    "sentences": ["First sentence.", "Second one.", ...],  # for BM25
    "hashes": {
        "url_hash": "9f86d081884c7d659a2feaa0c55ad015",      # xxhash.xxhash64(url).hexdigest()
        "content_hash": "a1b2c3d4e5f6...",                  # xxhash.xxhash64(content).hexdigest()
        "html_hash": "x9y8z7..."                          # optional
    },
    "timestamps": {
        "fetched_at": 1735689201,
        "cached_at": 1735689201,
        "expires_at": 1736294001,         # fetched_at + CACHE_DURATION
        "last_accessed": 1735689201,
        "access_count": 1
    },
    "fetch_success": true,
    "method": "trafilatura",
    "http_status": 200,
    "error_message": null
}
```

## Testing

Run the test suite:

```bash
python -m pytest cache/test_disk_cache.py
```