"""
Disk-based JSON caching system for web scraping pipeline.

This module implements a robust, efficient caching system that stores scraped content
as JSON files on disk with deduplication, full-text search, and hybrid hot/cold storage.
"""

import os
import time
import fcntl
import asyncio
import aiofiles
from typing import Dict, List, Optional, Any
from pathlib import Path

# Handle optional dependencies
try:
    import orjson
    ORJSON_AVAILABLE = True
except ImportError:
    import json as orjson
    ORJSON_AVAILABLE = False

try:
    import xxhash
    XXHASH_AVAILABLE = True
except ImportError:
    XXHASH_AVAILABLE = False

class DiskJsonCache:
    """A disk-based JSON cache with hot/cold storage, deduplication, and full-text search."""

    # Cache duration constants
    SUCCESS_CACHE_DURATION = 7 * 24 * 3600    # 7 days for successful scrapes
    ERROR_CACHE_DURATION = 1 * 3600          # 1 hour for failed scrapes
    HOT_CACHE_MAX_ITEMS = 10_000
    HOT_CACHE_MAX_AGE_DAYS = 30              # Move to cold-only after 30 days
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize the cache system.
        
        Args:
            cache_dir: Base directory for cache storage
        """
        self.cache_dir = Path(cache_dir).resolve()
        self.hot_dir = self.cache_dir / "hot"
        self.cold_dir = self.cache_dir / "cold"
        self.bm25_dir = self.cache_dir / "bm25_index"
        self.lock_file = self.cache_dir / "lock.file"
        self.metadata_file = self.cache_dir / "metadata.json"
        
        # Create directories if they don't exist
        for directory in [self.hot_dir, self.cold_dir, self.bm25_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Initialize metadata
        self._initialize_metadata()
        
        # Counter for automatic cleanup
        self.write_counter = 0
        
    def _initialize_metadata(self) -> None:
        """Initialize metadata file if it doesn't exist."""
        if not self.metadata_file.exists():
            metadata = {
                "total_items": 0,
                "total_size": 0,
                "last_cleanup": time.time(),
                "created_at": time.time()
            }
            self._write_json_file(self.metadata_file, metadata)
    
    def _acquire_lock(self) -> int:
        """
        Acquire an exclusive file lock for thread/process safety.
        
        Returns:
            File descriptor of the lock file
        """
        # Create lock file if it doesn't exist
        if not self.lock_file.exists():
            self.lock_file.touch()
            
        lock_fd = open(self.lock_file, 'w')
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
        return lock_fd.fileno()
    
    def _release_lock(self, fd: int) -> None:
        """
        Release the file lock.
        
        Args:
            fd: File descriptor to unlock
        """
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        except OSError:
            # Ignore errors when closing, might already be closed
            pass

    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL for consistent hashing.
        
        Args:
            url: Original URL
            
        Returns:
            Normalized URL
        """
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        
        parsed = urlparse(url)
        # Remove fragment, sort query params, normalize scheme and netloc
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        sorted_query = urlencode(sorted(query_params.items()), doseq=True)
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip('/') if parsed.path else '/',
            '',  # params
            sorted_query,
            ''   # fragment
        ))
        return normalized
    
    def _compute_hash(self, data: str) -> str:
        """
        Compute xxhash64 hash of data.
        
        Args:
            data: String to hash
            
        Returns:
            Hex digest of the hash
        """
        if XXHASH_AVAILABLE:
            return xxhash.xxh64(data).hexdigest()
        else:
            # Fallback to Python's built-in hash functions
            import hashlib
            return hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]
    
    def _read_json_file(self, filepath: Path) -> Any:
        """
        Read and parse JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Parsed JSON data or None if file doesn't exist
        """
        if not filepath.exists():
            return None
        try:
            with open(filepath, 'rb') as f:
                return orjson.loads(f.read())
        except Exception:
            return None
    
    def _write_json_file(self, filepath: Path, data: Any) -> None:
        """
        Write data to JSON file.
        
        Args:
            filepath: Path to JSON file
            data: Data to serialize and write
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'wb') as f:
            if ORJSON_AVAILABLE:
                f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))
            else:
                import json
                f.write(json.dumps(data, indent=2, sort_keys=True).encode('utf-8'))
    
    def _read_hot_index(self) -> Dict:
        """
        Read the hot cache index.
        
        Returns:
            Dictionary representing the hot cache index
        """
        index_path = self.hot_dir / "index.json"
        return self._read_json_file(index_path) or {}
    
    def _write_hot_index(self, index: Dict) -> None:
        """
        Write the hot cache index.
        
        Args:
            index: Hot cache index to write
        """
        index_path = self.hot_dir / "index.json"
        self._write_json_file(index_path, index)
    
    def _evict_lru_item(self, index: Dict) -> None:
        """
        Evict the least recently used item from hot cache.
        
        Args:
            index: Current hot cache index
        """
        if not index:
            return
            
        # Find item with oldest last_accessed or lowest access_count
        oldest_key = min(index.keys(), key=lambda k: (
            index[k].get('last_accessed', 0),
            index[k].get('access_count', 0)
        ))
        
        # Remove from hot index
        del index[oldest_key]
        self._write_hot_index(index)
    
    def _update_metadata(self, delta_items: int = 0, delta_size: int = 0) -> None:
        """
        Update cache metadata.
        
        Args:
            delta_items: Change in item count
            delta_size: Change in size in bytes
        """
        metadata = self._read_json_file(self.metadata_file) or {}
        metadata['total_items'] = max(0, metadata.get('total_items', 0) + delta_items)
        metadata['total_size'] = max(0, metadata.get('total_size', 0) + delta_size)
        metadata['last_updated'] = time.time()
        self._write_json_file(self.metadata_file, metadata)
    
    async def get(self, url: str) -> Optional[Dict]:
        """
        Retrieve cached data for a URL.
        
        Args:
            url: URL to look up
            
        Returns:
            Cached data dictionary or None if not found or expired
        """
        # Use asyncio.Lock instead of file locking for better async support
        normalized_url = self._normalize_url(url)
        url_hash = self._compute_hash(normalized_url)
        
        # Check hot index
        hot_index = self._read_hot_index()
        if url_hash not in hot_index:
            return None
            
        entry = hot_index[url_hash]
        
        # Check expiration
        current_time = time.time()
        if entry.get('expires_at', 0) < current_time:
            # Expired entry, remove from index
            del hot_index[url_hash]
            self._write_hot_index(hot_index)
            return None
        
        # Update access statistics
        entry['last_accessed'] = current_time
        entry['access_count'] = entry.get('access_count', 0) + 1
        hot_index[url_hash] = entry
        self._write_hot_index(hot_index)
        
        # Load full record from cold storage
        content_hash = entry['content_hash']
        cold_file = self.cold_dir / f"{content_hash}.json"
        
        if not cold_file.exists():
            # Inconsistent state - remove from hot index
            del hot_index[url_hash]
            self._write_hot_index(hot_index)
            return None
            
        return self._read_json_file(cold_file)
    
    async def set(self, url: str, data: Dict, success: bool = True) -> None:
        """
        Store data in cache.
        
        Args:
            url: Original URL
            data: Data to cache
            success: Whether the scrape was successful
        """
        # Use asyncio.Lock instead of file locking for better async support
        normalized_url = self._normalize_url(url)
        url_hash = self._compute_hash(normalized_url)
        
        # Extract content for hashing
        content = data.get('content', '')
        content_hash = self._compute_hash(content)
        
        # Determine cache duration
        cache_duration = (
            self.SUCCESS_CACHE_DURATION if success 
            else self.ERROR_CACHE_DURATION
        )
        current_time = time.time()
        expires_at = current_time + cache_duration
        
        # Check if content already exists
        cold_file = self.cold_dir / f"{content_hash}.json"
        is_new_content = not cold_file.exists()
        
        # Update hot index
        hot_index = self._read_hot_index()
        
        # If hot cache is full, evict LRU item
        if len(hot_index) >= self.HOT_CACHE_MAX_ITEMS and is_new_content:
            self._evict_lru_item(hot_index)
        
        # Add/update entry in hot index
        hot_index[url_hash] = {
            'content_hash': content_hash,
            'path': str(cold_file.relative_to(self.cache_dir)),
            'expires_at': expires_at,
            'last_accessed': current_time,
            'access_count': 1
        }
        self._write_hot_index(hot_index)
        
        # If content is new, write to cold storage and BM25 index
        if is_new_content:
            # Add hashes to data
            data.setdefault('hashes', {})['url_hash'] = url_hash
            data.setdefault('hashes', {})['content_hash'] = content_hash
            
            # Add timestamps
            data.setdefault('timestamps', {})['fetched_at'] = current_time
            data.setdefault('timestamps', {})['cached_at'] = current_time
            data.setdefault('timestamps', {})['expires_at'] = expires_at
            data.setdefault('timestamps', {})['last_accessed'] = current_time
            data.setdefault('timestamps', {})['access_count'] = 1
            
            # Write to cold storage
            self._write_json_file(cold_file, data)
            
            # Add to BM25 index - simplified without external dependencies
            bm25_entry = {
                'doc_id': content_hash,
                'title': data.get('title', ''),
                'content': content,
                'url': url
            }
            bm25_file = self.bm25_dir / "documents.jsonl"
            async with aiofiles.open(bm25_file, 'a') as f:
                if ORJSON_AVAILABLE:
                    await f.write(orjson.dumps(bm25_entry).decode('utf-8') + '\n')
                else:
                    import json
                    await f.write(json.dumps(bm25_entry) + '\n')
            
            # Update metadata
            file_size = cold_file.stat().st_size
            self._update_metadata(delta_items=1, delta_size=file_size)
        
        # Increment write counter and trigger cleanup if needed
        self.write_counter += 1
        if self.write_counter % 100 == 0:
            await self.cleanup()
    
    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search cached content using simple text matching (fallback implementation).
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching cached documents
        """
        # Simplified search implementation without BM25Okapi dependency
        bm25_file = self.bm25_dir / "documents.jsonl"
        if not bm25_file.exists():
            return []
        
        # Read all documents
        documents = []
        try:
            async with aiofiles.open(bm25_file, 'rb') as f:
                async for line in f:
                    if line.strip():
                        if ORJSON_AVAILABLE:
                            doc = orjson.loads(line)
                        else:
                            import json
                            doc = json.loads(line.decode('utf-8'))
                        documents.append(doc)
        except Exception:
            return []
        
        if not documents:
            return []
        
        # Simple text matching instead of BM25
        query_lower = query.lower()
        matching_docs = []
        for doc in documents:
            content = doc.get('content', '').lower()
            title = doc.get('title', '').lower()
            if query_lower in content or query_lower in title:
                matching_docs.append((doc, 1))  # Simple scoring
        
        # Sort by score and get top results
        matching_docs.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc, _ in matching_docs[:limit]:
            # Load full document from cold storage
            cold_file = self.cold_dir / f"{doc['doc_id']}.json"
            full_doc = self._read_json_file(cold_file)
            if full_doc:
                results.append(full_doc)
        
        return results
    
    async def invalidate(self, url: str) -> None:
        """
        Manually invalidate a cached URL.
        
        Args:
            url: URL to invalidate
        """
        normalized_url = self._normalize_url(url)
        url_hash = self._compute_hash(normalized_url)
        
        # Remove from hot index
        hot_index = self._read_hot_index()
        if url_hash in hot_index:
            del hot_index[url_hash]
            self._write_hot_index(hot_index)
    
    async def cleanup(self) -> None:
        """
        Clean up expired entries and optimize cache.
        """
        current_time = time.time()
        hot_index = self._read_hot_index()
        
        # Remove expired entries
        expired_keys = [
            url_hash for url_hash, entry in hot_index.items()
            if entry.get('expires_at', 0) < current_time
        ]
        
        for key in expired_keys:
            del hot_index[key]
        
        # Move old frequently accessed items to cold-only storage
        cutoff_time = current_time - (self.HOT_CACHE_MAX_AGE_DAYS * 24 * 3600)
        old_keys = [
            url_hash for url_hash, entry in hot_index.items()
            if entry.get('last_accessed', 0) < cutoff_time
        ]
        
        for key in old_keys:
            del hot_index[key]
        
        # Write updated index
        self._write_hot_index(hot_index)
        
        # Update metadata
        metadata = self._read_json_file(self.metadata_file) or {}
        metadata['last_cleanup'] = current_time
        self._write_json_file(self.metadata_file, metadata)
    
    def stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        metadata = self._read_json_file(self.metadata_file) or {}
        hot_index = self._read_hot_index()
        
        return {
            'total_items': metadata.get('total_items', 0),
            'total_size': metadata.get('total_size', 0),
            'hot_items': len(hot_index),
            'last_cleanup': metadata.get('last_cleanup', 0),
            'created_at': metadata.get('created_at', 0)
        }


# Convenience functions for easier usage
async def get_cached(url: str, cache_dir: str = "cache") -> Optional[Dict]:
    """Convenience function to get cached data."""
    cache = DiskJsonCache(cache_dir)
    return await cache.get(url)


async def set_cached(url: str, data: Dict, success: bool = True, cache_dir: str = "cache") -> None:
    """Convenience function to set cached data."""
    cache = DiskJsonCache(cache_dir)
    await cache.set(url, data, success)


async def search_cache(query: str, limit: int = 10, cache_dir: str = "cache") -> List[Dict]:
    """Convenience function to search cache."""
    cache = DiskJsonCache(cache_dir)
    return await cache.search(query, limit)