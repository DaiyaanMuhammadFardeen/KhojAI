#!/usr/bin/env python3
"""
Comprehensive testing and debugging script for search_utils.py
Tests each component independently and together.
"""

import sys
import os
import warnings

# Add the AI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Suppress ResourceWarning
warnings.filterwarnings("ignore", category=ResourceWarning)

from search_utils import (
    search_web, 
    scrape_webpage, 
    extract_relevant_information, 
    search_and_extract
)
from duckduckgo_search import DDGS

def test_duckduckgo_direct():
    """Test DuckDuckGo search directly using the duckduckgo-search library."""
    print("=" * 60)
    print("TESTING DUCKDUCKGO DIRECTLY")
    print("=" * 60)
    
    try:
        print("1. Testing DDGS context manager...")
        with DDGS() as ddgs:
            print("   ✓ DDGS context manager works")
            
            print("2. Testing basic search...")
            results = list(ddgs.text("Python programming", max_results=3))
            print(f"   ✓ Found {len(results)} results")
            
            if results:
                print("3. Examining result structure...")
                for i, result in enumerate(results[:2]):
                    print(f"   Result {i+1}:")
                    for key, value in result.items():
                        print(f"     {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
            else:
                print("   ✗ No results found")
                
        return True
    except Exception as e:
        print(f"   ✗ Error testing DuckDuckGo directly: {e}")
        return False

def test_search_web():
    """Test the search_web function."""
    print("\n" + "=" * 60)
    print("TESTING search_web FUNCTION")
    print("=" * 60)
    
    test_queries = [
        "Python programming",
        "machine learning basics",
        "weather in Tokyo"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Testing search for: '{query}'")
        try:
            # Test DuckDuckGo search
            print("   a. Testing DuckDuckGo search...")
            ddg_results = search_web(query, num_results=3, engine="duckduckgo")
            print(f"      ✓ DuckDuckGo returned {len(ddg_results)} URLs")
            if ddg_results:
                for j, url in enumerate(ddg_results):
                    print(f"        URL {j+1}: {url}")
            
            # Test Google search (fallback)
            print("   b. Testing Google search (fallback)...")
            google_results = search_web(query, num_results=3, engine="google_scrape")
            print(f"      ✓ Google returned {len(google_results)} URLs")
            if google_results:
                for j, url in enumerate(google_results):
                    print(f"        URL {j+1}: {url}")
                    
        except Exception as e:
            print(f"      ✗ Error: {e}")

def test_scrape_webpage():
    """Test the scrape_webpage function."""
    print("\n" + "=" * 60)
    print("TESTING scrape_webpage FUNCTION")
    print("=" * 60)
    
    test_urls = [
        "https://httpbin.org/html",  # Simple test page
        "https://example.com",       # Basic example site
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"{i}. Testing scrape of: {url}")
        try:
            result = scrape_webpage(url, max_content_length=1000)
            print(f"   ✓ Scraped successfully")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Content preview: {result.get('content', 'N/A')[:200]}...")
            print(f"   URL: {result.get('url', 'N/A')}")
        except Exception as e:
            print(f"   ✗ Error scraping {url}: {e}")

def test_extract_relevant_information():
    """Test the extract_relevant_information function."""
    print("\n" + "=" * 60)
    print("TESTING extract_relevant_information FUNCTION")
    print("=" * 60)
    
    # Sample content for testing
    sample_content = """
    Python is a high-level programming language. It is widely used for web development.
    Machine learning is a subset of artificial intelligence. Python is great for machine learning.
    Data science involves statistics and programming. Many data scientists use Python.
    Web development can be done with various technologies. JavaScript is popular for front-end.
    """
    
    test_keywords = [
        ["Python", "programming"],
        ["machine learning"],
        ["web development", "JavaScript"]
    ]
    
    for i, keywords in enumerate(test_keywords, 1):
        print(f"{i}. Testing extraction with keywords: {keywords}")
        try:
            sentences = extract_relevant_information(sample_content, keywords)
            print(f"   ✓ Found {len(sentences)} relevant sentences")
            for j, sentence in enumerate(sentences, 1):
                print(f"     {j}. {sentence}")
        except Exception as e:
            print(f"   ✗ Error: {e}")

def test_search_and_extract():
    """Test the search_and_extract function."""
    print("\n" + "=" * 60)
    print("TESTING search_and_extract FUNCTION")
    print("=" * 60)
    
    test_cases = [
        ("Python programming basics", ["Python", "programming"]),
        ("machine learning applications", ["machine learning", "AI"]),
    ]
    
    for i, (query, keywords) in enumerate(test_cases, 1):
        print(f"{i}. Testing search and extract for: '{query}'")
        print(f"   Keywords: {keywords}")
        try:
            results = search_and_extract(query, keywords)
            print(f"   ✓ Found {len(results)} sources with relevant information")
            for j, result in enumerate(results):
                print(f"     Source {j+1}:")
                print(f"       Title: {result.get('title', 'N/A')}")
                print(f"       URL: {result.get('url', 'N/A')}")
                print(f"       Relevant sentences: {len(result.get('relevant_sentences', []))}")
                if result.get('relevant_sentences'):
                    print(f"       Sample: {result['relevant_sentences'][0][:100]}...")
        except Exception as e:
            print(f"   ✗ Error: {e}")

def test_integration():
    """Test the complete integration of all components."""
    print("\n" + "=" * 60)
    print("TESTING COMPLETE INTEGRATION")
    print("=" * 60)
    
    test_query = "Python web frameworks"
    test_keywords = ["Python", "web", "frameworks"]
    
    print(f"Testing complete workflow with query: '{test_query}'")
    print(f"Keywords: {test_keywords}")
    
    try:
        print("1. Searching web...")
        urls = search_web(test_query, num_results=3)
        print(f"   ✓ Found {len(urls)} URLs")
        
        if urls:
            print("2. Scraping first URL...")
            page_data = scrape_webpage(urls[0], max_content_length=2000)
            print(f"   ✓ Scraped: {page_data.get('title', 'N/A')}")
            
            print("3. Extracting relevant information...")
            relevant_info = extract_relevant_information(page_data.get('content', ''), test_keywords)
            print(f"   ✓ Found {len(relevant_info)} relevant sentences")
            
            print("4. Testing full search_and_extract...")
            full_results = search_and_extract(test_query, test_keywords)
            print(f"   ✓ Full process returned {len(full_results)} sources")
            
    except Exception as e:
        print(f"   ✗ Error in integration test: {e}")

def main():
    """Run all tests."""
    print("SEARCH UTILS COMPREHENSIVE TESTING SCRIPT")
    print("This script will test all components of search_utils.py")
    
    # Run all tests
    duckduckgo_works = test_duckduckgo_direct()
    test_search_web()
    test_scrape_webpage()
    test_extract_relevant_information()
    test_search_and_extract()
    test_integration()
    
    print("\n" + "=" * 60)
    print("TESTING SUMMARY")
    print("=" * 60)
    if duckduckgo_works:
        print("✓ DuckDuckGo interface is working correctly")
    else:
        print("✗ DuckDuckGo interface has issues")
    print("✓ All search_utils.py functions tested")
    print("Run completed. Check output above for details.")

if __name__ == "__main__":
    main()