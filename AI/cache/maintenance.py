#!/usr/bin/env python3
"""
Cache maintenance utilities for the disk-based JSON cache system.

Provides commands for cleaning up expired entries, rebuilding BM25 index,
showing statistics, and optimizing storage.
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Handle optional dependencies
try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    import json as orjson
    ORJSON_AVAILABLE = False

from cache.disk_cache import DiskJsonCache


def cleanup_cache(cache_dir: str = "cache") -> None:
    """Remove expired entries from cache."""
    print("Running cache cleanup...")
    cache = DiskJsonCache(cache_dir)
    import asyncio
    asyncio.run(cache.cleanup())
    print("Cache cleanup completed.")


def rebuild_bm25_index(cache_dir: str = "cache") -> None:
    """Rebuild the search index from cold storage."""
    print("Rebuilding search index...")
    cache = DiskJsonCache(cache_dir)
    cold_dir = Path(cache_dir) / "cold"
    bm25_file = Path(cache_dir) / "bm25_index" / "documents.jsonl"
    
    # Clear existing index
    bm25_file.unlink(missing_ok=True)
    
    # Rebuild from cold storage
    count = 0
    for file_path in cold_dir.glob("*.json"):
        try:
            with open(file_path, 'rb') as f:
                if ORJSON_AVAILABLE:
                    data = orjson.loads(f.read())
                else:
                    import json
                    data = json.loads(f.read().decode('utf-8'))
                
            # Create entry
            bm25_entry = {
                'doc_id': data.get('hashes', {}).get('content_hash', ''),
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'url': data.get('url', '')
            }
            
            # Append to index
            with open(bm25_file, 'a') as f:
                if ORJSON_AVAILABLE:
                    f.write(orjson.dumps(bm25_entry).decode('utf-8') + '\n')
                else:
                    import json
                    f.write(json.dumps(bm25_entry) + '\n')
            
            count += 1
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {e}")
    
    print(f"Search index rebuilt with {count} documents.")


def show_stats(cache_dir: str = "cache") -> None:
    """Display cache statistics."""
    cache = DiskJsonCache(cache_dir)
    stats = cache.stats()
    
    print("Cache Statistics:")
    print(f"  Total Items: {stats['total_items']}")
    print(f"  Hot Items: {stats['hot_items']}")
    print(f"  Total Size: {stats['total_size']:,} bytes ({stats['total_size'] / (1024*1024):.2f} MB)")
    print(f"  Last Cleanup: {stats['last_cleanup']}")
    print(f"  Created At: {stats['created_at']}")


def vacuum_cache(cache_dir: str = "cache") -> None:
    """Perform full cache optimization."""
    print("Vacuuming cache...")
    cleanup_cache(cache_dir)
    rebuild_bm25_index(cache_dir)
    show_stats(cache_dir)
    print("Cache vacuum completed.")


def main():
    parser = argparse.ArgumentParser(description="Cache maintenance utilities")
    parser.add_argument(
        "command",
        choices=["cleanup", "reindex-bm25", "vacuum", "stats"],
        help="Maintenance command to execute"
    )
    parser.add_argument(
        "--cache-dir",
        default="cache",
        help="Cache directory path (default: cache)"
    )
    
    args = parser.parse_args()
    
    if args.command == "cleanup":
        cleanup_cache(args.cache_dir)
    elif args.command == "reindex-bm25":
        rebuild_bm25_index(args.cache_dir)
    elif args.command == "vacuum":
        vacuum_cache(args.cache_dir)
    elif args.command == "stats":
        show_stats(args.cache_dir)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()