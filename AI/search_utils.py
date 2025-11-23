#search_utils.py
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from typing import List, Dict
import time
import re
import random
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
import difflib
import warnings

# Configuration flagto disableGoogle scraping (it's brittle and legally risky)
ALLOW_GOOGLE_SCRAPE = False  # Set to True only for dev/testing

# Import configuration from prompt_analyzer
try:
    from prompt_analyzer import SEARCH_ENGINE, MAX_SEARCH_QUERIES, MAX_SEARCH_RESULTS
except ImportError:
    # Default values if not available
    SEARCH_ENGINE = "duckduckgo"
    MAX_SEARCH_QUERIES = 3
    MAX_SEARCH_RESULTS = 5  # Increased from 3 to 5

def extract_relevant_information(content: str, keywords: List[str]) -> List[str]:
    """
    Extract sentences that are relevant to the givenkeywords.
"""
    # RemoveHTML tags
    content = re.sub(r'<[^>]*>', ' ', content)
    # Normalize multiple whitespaces, newlines, etc., to single spaces
    content = re.sub(r'\s+', ' ', content).strip()
    
    # Split content into sentences
    # Better split: Handles sentences endingwith .!? followed by space, avoiding abbreviations like Mr./Dr.
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', content)
    
    print(f"Split content into {len(sentences)} sentences.")
    
    relevant_sentences = []
    keywords_lower = [kw.lower() for kw in keywords]
    
    # Optional: For whole-word matching, use word boundaries (e.g., \bkey\b to avoid matching "monkey")
    # But keep substring for broader results; toggle if needed
    whole_word= False  # Set to True for stricter matching
    if whole_word:
        keyword_patterns = [re.compile(r'\b' + re.escape(kw) + r'\b') for kw in keywords_lower]
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 5: # Allow shorter sentences, like web snippets or titles
            continue
            
        # Check if sentence contains any keywords
        sentence_lower = sentence.lower()
        if whole_word:
            if any(pattern.search(sentence_lower) for pattern in keyword_patterns):
                relevant_sentences.append(sentence)
        else:
            if any(kw in sentence_lower for kw in keywords_lower):
                relevant_sentences.append(sentence)
    
    # Sort by number of keyword matches (descending)
    relevant_sentences.sort(key=lambda s: sum(1 for kw in keywords_lower if kw in s.lower()), reverse=True)
    print(f"Found {len(relevant_sentences)} relevant sentences outof {len(sentences)} total.")
    return relevant_sentences[:10]  # Return top 10 relevant sentences

def search_web(query: str, num_results: int = 3, engine: str = SEARCH_ENGINE) -> List[str]:
    """Flexible search: DuckDuckGo primary, Google fallback."""
    if engine == "duckduckgo":
        try:
            #Use context manager to ensure proper resource handling
            with DDGS(timeout=30) as ddgs:  # Increased timeout to 30 seconds
                results = ddgs.text(query, max_results=num_results)
                urls = [r["href"] for r in results if r.get("href") and r["href"].startswith("http")]
                if not urls:
                    raise ValueError("No results returned from DuckDuckGo")  # Force fallback or log
                time.sleep(random.uniform(0.5, 1.5))  # Shorter sleep, only on success
                return urls
        except Exception as e:
            print(f"[DDG Error] {e}")
            return search_web(query, num_results,engine="google_scrape")  # Fallback
    
    elif engine == "google_scrape":
        if not ALLOW_GOOGLE_SCRAPE:
            print("[Google] Scraping disabled via config")
            return []
        try:
            # Enhanced scraping with better evasion
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (X11;Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
            headers = {'User-Agent': random.choice(user_agents)}
            search_url =f"https://www.google.com/search?q={query.replace(' ', '+')}&num={num_results}"
            response = requests.get(search_url, headers=headers, timeout=30)  # Increased timeout to 30 seconds
            
            # Check robots.txt compliance - Fixed robots URL
            rp = RobotFileParser()
            rp.set_url("https://www.google.com/robots.txt")
            rp.read()
            if not rp.can_fetch(headers['User-Agent'], "/search"):
                raise ValueError("Blocked by robots.txt")
            
            # Update parser for modern Google HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            for result in soup.select('div.tF2Cxc a')[:num_results]:  # Better selector
                href = result.get('href')
                if href and href.startswith('http'):
                    links.append(href)
            return links
        except Exception as e:
            print(f"[Google Error] {e}")
            return []

def scrape_webpage(url: str, max_content_length: int = 5000) -> Dict[str, str]:
    """Scrape content from a webpage with robots.txt compliance."""
    try:
        # Check robots.txt compliance
        rp = RobotFileParser()
        rp.set_url(urljoin(url,'/robots.txt'))
        rp.read()
        # Fixed invalid User-Agent - now using actual header User-Agent
        if not rp.can_fetch(requests.utils.default_headers()['User-Agent'], url):
            return {"url": url, "title": "Blocked", "content": "Disallowed by robots.txt"}
            
        user_agents =[
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        headers = {'User-Agent': random.choice(user_agents)}
        response= requests.get(url, headers=headers, timeout=30)  # Increased timeout to 30 seconds
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Gettitle
        title = soup.title.string if soup.title else "No title"
        
        # Get main content
        # Try to find main content area
        content_areas = soup.find_all(['main', 'article', 'div', 'p'])
        content = ""
        
        # Prioritize main/article tags, thendivs, then paragraphs
        main_content = soup.find('main') or soup.find('article')
        if main_content:
            content = main_content.get_text(separator=' ', strip=True)
        else:
            # Try to get content from divs with common content classes
            content_divs = soup.find_all('div', class_=re.compile(r'content|main|article|post', re.I))
            if content_divs:
                content = content_divs[0].get_text(separator=' ', strip=True)
            else:
                # Fallback to body content
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
        
        # Limit content length
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        return {
            "url": url,
            "title": title.strip(),
            "content": content.strip()
}
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {
            "url": url,
            "title": "Error",
            "content": f"Failed to scrape content: {str(e)}"
        }

def search_and_extract(query: str, keywords: List[str]) -> List[Dict[str, str]]:
    """
    Perform web search and extract relevant information.
    """
    urls = search_web(query, num_results=MAX_SEARCH_RESULTS)  # Using configurable constant
    
    # Deduplicate URLs
    seen = set()
    urls = [u for u in urls if u not in seen and not seen.add(u)]
    
    print(f"Found {len(urls)} unique URLs after deduplication.")
    
    information_table = []
    
    # Process only top 5 URLs max to avoid timeouts
    for url in urls[:5]:
        try:
            page_data = scrape_webpage(url)
            print(f"Scraped {url}: Content length = {len(page_data.get('content', '')) if 'content' in page_data else 'No content key'}")
            
            if not isinstance(page_data, dict) or "url" not in page_data or "title" not in page_data or "content" not in page_data:
                print(f"Invalid page_data format for {url}. Skipping.")
                continue
            if not page_data["content"] or len(page_data["content"]) < 100:  # Arbitrary threshold for minimal content
                print(f"Empty or too short content for {url}. Skipping.")
                continue
                
            if"content" not in page_data:
                print(f"Warning: No 'content' key in page_data for {url}")
                continue  # Add this to skip if no content
            
            if "Failed" not in page_data["content"] and "Blocked" not in page_data["content"]:
                relevant_info =extract_relevant_information(page_data["content"], keywords)
                print(f"Extracted {len(relevant_info)} relevant sentences for {url}")
                if relevant_info:
                    information_table.append({
                        "url": page_data["url"], 
                        "title": page_data["title"],
                        "relevant_sentences": relevant_info[:10]  # Increased from 5 to 10
                    })
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            continue
            
        time.sleep(random.uniform(1.0, 2.0))  # Increased sleep to avoid blocks
    return information_table


def main():
    """
    Test all functions in this module with simple examples.
    """
    print("=" * 60)
    print("Testing search_utils.py functions")
    print("=" * 60)
    
    # Test 1: extract_relevant_information
    print("\n1. Testing extract_relevant_information function:")
    sample_content = "Python is a high-level programming language. It is widely used for web development. " \
                     "Machine learning is a subset of artificial intelligence. Python is great for machine learning."
    keywords = ["Python", "programming"]
    relevant_sentences = extract_relevant_information(sample_content, keywords)
    print(f"   Content: {sample_content}")
    print(f"   Keywords: {keywords}")
    print(f"   Relevant sentences found: {len(relevant_sentences)}")
    for i, sentence in enumerate(relevant_sentences, 1):
        print(f"     {i}. {sentence}")
    
   # Test 2: search_web
    print("\n2. Testing search_web function:")
    try:
        urls = search_web("Python programming", num_results=2, engine="duckduckgo")
        print(f"   Found {len(urls)} URLs:")
        for i, url in enumerate(urls, 1):
            print(f"     {i}. {url}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: scrape_webpage
    print("\n3. Testing scrape_webpage function:")
    try:
        page_data = scrape_webpage("https://httpbin.org/html")
        print(f"   Title: {page_data.get('title', 'N/A')}")
        print(f"   URL: {page_data.get('url', 'N/A')}")
        content_preview = page_data.get('content', 'N/A')[:100] + "..." if len(page_data.get('content', '')) > 100 else page_data.get('content', 'N/A')
        print(f"   Content preview: {content_preview}")
    except Exception as e:
        print(f"   Error: {e}")
    # Test 4: search_and_extract
    print("\n4. Testing search_and_extract function:")
    try:
        results = search_and_extract("Python programming", ["Python", "programming"])
        print(f"   Found information from {len(results)} sources:")
        for i, result in enumerate(results[:2], 1): # Limit to 2 results for brevity
            print(f"     {i}. Title: {result.get('title', 'N/A')}")
            print(f"        URL: {result.get('url', 'N/A')}")
            print(f"        Relevant sentences: {len(result.get('relevant_sentences', []))}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Finished testing search_utils.py functions")
    print("=" * 60)


if __name__ == "__main__":
    main()