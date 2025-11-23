import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import re
from urllib.parse import urljoin, urlparse

def search_web(query: str, num_results: int = 2) -> List[str]:
    """
    Perform a web search and return top URLs.
    For now,we'll simulate this with a simple Google search.
    In production, you might want to use a proper search API.
    """
    try:
        # This is a simple approach - in production, use a proper search API
        search_url = f"https://www.google.com/search?q={query}&num={num_results}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract URLs from search results
        links = []
        for g in soup.find_all('div', class_='g'):
            anchor = g.find('a')
            if anchor and anchor.get('href'):
                link = anchor.get('href')
                if link.startswith('/url?q='):
                    # Extract actual URL from Google's redirect
                    link = link.split('/url?q=')[1].split('&')[0]
                if link and link.startswith('http'):
                    links.append(link)
                    if len(links) >= num_results:
                        break
        
        return links[:num_results]
    except Exception as e:
        print(f"Error performing web search: {e}")
        return []

def scrape_webpage(url: str, max_content_length: int = 5000) -> Dict[str, str]:
    """
    Scrape content from a webpage.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get title
        title = soup.title.string if soup.title else "No title"
        
        # Get main content
        # Try to find main content area
        content_areas = soup.find_all(['main', 'article', 'div', 'p'])
        content = ""
        
        # Prioritize main/article tags, then divs, then paragraphs
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
                    content = body.get_text(separator='', strip=True)
        
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

def extract_relevant_information(content: str, keywords: List[str]) -> List[str]:
    """
Extract sentences that are relevant to the given keywords.
    """
    # Split content into sentences
    sentences = re.split(r'[.!?]+', content)
    
    relevant_sentences = []
    keywords_lower = [kw.lower() for kw in keywords]
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:  # Skip very short sentences
            continue
            
        # Check if sentence contains any keywords
        sentence_lower = sentence.lower()
        if any(kw in sentence_lower for kw in keywords_lower):
            relevant_sentences.append(sentence)
    
    return relevant_sentences[:10] # Return top 10 relevant sentences

def search_and_extract(query: str, keywords: List[str]) -> List[Dict[str, str]]:
    """
    Perform web search and extract relevant information.
    """
    #Use the improved search_and_extract from search_utils
    from search_utils import search_and_extract as improved_search_and_extract
    return improved_search_and_extract(query, keywords)
