# web_search.py
import os
import requests
from typing import List, Dict
import time
import random
import asyncio
from dotenv import load_dotenv
from search_utils import extract_relevant_information
from scrape_util import scrape_webpage

# Load environment variables from .env
load_dotenv()

# Import cache functionality
from cache.disk_cache import DiskJsonCache

# === CONFIGURATION FROM .env ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")  # Search Engine ID
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
MAX_CONCURRENT_SCRAPES = int(os.getenv("MAX_CONCURRENT_SCRAPES", "3"))

# Initialize cache
cache = DiskJsonCache("cache")

# Validate required credentials
if not GOOGLE_API_KEY or not GOOGLE_CX:
    raise EnvironmentError(
        "Missing GOOGLE_API_KEY or GOOGLE_CX in .env file. "
        "Please check your .env configuration."
    )

# === CORE FUNCTIONS ===

def search_web(query: str, num_results: int = MAX_SEARCH_RESULTS) -> List[str]:
    """
    Search using Google Programmable Search Engine (Custom Search JSON API).
    Returns list of URLs.
    """
    if num_results > 10:
        print(f"Warning: Google API limits num to 10. Requested {num_results}, using 10.")
        num_results = 10

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": num_results
    }

    # Retry logic for rate limiting and transient errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Searching Google PSE: '{query}' (max {num_results} results)")
            response = requests.get(url, params=params, timeout=10)
            
            # Handle rate limiting
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    print(f"Rate limited. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("Google API Error: Rate limit exceeded. Max retries reached.")
                    return []
            
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            urls = []
            for item in items:
                link = item.get("link")
                if link and link.startswith("http"):
                    urls.append(link)

            if not urls:
                print("No valid URLs returned from Google PSE.")
            else:
                print(f"Found {len(urls)} valid URLs from Google PSE.")

            return urls

        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                print("Google API Error: Quota exceeded or invalid API key.")
                # Don't retry on auth errors
                break
            elif response.status_code == 400:
                print("Google API Error: Bad request (check query or CX).")
                # Don't retry on bad requests
                break
            elif response.status_code == 429:
                # Already handled above
                pass
            else:
                print(f"Google API HTTP Error: {response.status_code} - {e}")
                if attempt < max_retries - 1:
                    # Wait before retry
                    wait_time = 2 ** attempt
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
        except requests.exceptions.RequestException as e:
            print(f"Network error during Google search: {e}")
            if attempt < max_retries - 1:
                # Wait before retry
                wait_time = 2 ** attempt
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
        except Exception as e:
            print(f"Unexpected error in search_web(): {e}")
            if attempt < max_retries - 1:
                # Wait before retry
                wait_time = 2 ** attempt
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

    return []

async def search_and_extract(query: str, keywords: List[str]) -> List[Dict[str, str]]:
    """Main function: search → scrape → extract relevant info with improved concurrency."""
    print(f"\nStarting search_and_extract: '{query}'")
    
    # First, try to get results from cache
    cached_results = await cache.search(query, limit=5)
    if cached_results:
        print(f"Found {len(cached_results)} results in cache")
        # Process cached results
        results = []
        for cached_page in cached_results:
            relevant = extract_relevant_information(cached_page["content"], keywords, top_n=5)
            if relevant:
                # Convert the new format (sentence, score, metadata) to the old format for compatibility
                relevant_sentences = [(sentence, score, metadata) for sentence, score, metadata in relevant]
                results.append({
                    "url": cached_page["url"],
                    "title": cached_page["title"],
                    "relevant_sentences": relevant_sentences
                })
        if results:
            print(f"Using {len(results)} cached results")
            return results

    urls = search_web(query, num_results=MAX_SEARCH_RESULTS)

    if not urls:
        print("No URLs found. Returning empty results.")
        return []

    # Deduplicate
    seen = set()
    urls = [u for u in urls if u not in seen and not seen.add(u)]
    print(f"Processing {len(urls)} unique URLs...")

    # Process URLs concurrently with a semaphore to limit concurrency
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_SCRAPES)  # Configurable concurrency limit
    
    async def process_url(url):
        async with semaphore:
            print(f"Processing: {url}")
            
            # Check if page is already cached
            cached_page = await cache.get(url)
            if cached_page:
                print(f"Using cached content for {url}")
                page = cached_page
            else:
                page = await scrape_webpage(url)
                # Cache the scraped page
                await cache.set(url, page, success=bool(page.get("content")))

            if not page["content"] or len(page["content"]) < 100:
                print(f"Skipping {url}: too short or failed.")
                return None

            if "failed" in page["content"].lower() or "blocked" in page["content"].lower():
                return None

            # Updated to use the new extract_relevant_information function
            relevant = extract_relevant_information(page["content"], keywords, top_n=5)
            if relevant:
                # Convert the new format (sentence, score, metadata) to the old format for compatibility
                relevant_sentences = [(sentence, score, metadata) for sentence, score, metadata in relevant]
                result = {
                    "url": page["url"],
                    "title": page["title"],
                    "relevant_sentences": relevant_sentences
                }
                print(f"Added {len(relevant)} relevant sentences from {url}")
                return result
            return None
    
    # Create tasks for all URLs
    tasks = [process_url(url) for url in urls[:5]]  # Limit to top 5
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out None results and exceptions
    results = [r for r in results if r is not None and not isinstance(r, Exception)]
    
    print(f"Completed. Found {len(results)} useful sources.\n")
    return results


# === TEST FUNCTION ===
def main():
    print("=" * 60)
    print("Google Programmable Search Engine + Scraper Test")
    print("=" * 60)

    test_query = "Who is the current President of the United States in 2025"
    keywords = ["president", "current", "United States", "America", "2025"]

    results = asyncio.run(search_and_extract(test_query, keywords))

    for i, res in enumerate(results, 1):
        print(f"\n{i}. {res['title']}")
        print(f"    URL: {res['url']}")
        print(f"    Relevant: {len(res['relevant_sentences'])} sentences")
        # Updated to handle the new format (sentence, score, metadata)
        for sentence, score, metadata in res['relevant_sentences'][:2]:
            print(f"      • [Score: {score:.2f}] {sentence}")
            print(f"        Metadata: BM25={metadata['bm25_score']}, "
                  f"Keywords={metadata['original_matches']}, "
                  f"Expanded={metadata['expanded_matches']}, "
                  f"Entities={metadata['entity_overlap']}")

    print("\nTest complete.")


if __name__ == "__main__":
    main()
