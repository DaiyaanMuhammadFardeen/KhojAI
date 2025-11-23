#!/usr/bin/env python3
"""
Test script for search_utils.py functions
"""

import sys
import os

# Add the AI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from search_utils import (
    extract_relevant_information,
    search_web,
    scrape_webpage,
    search_and_extract
)

def test_extract_relevant_information():
    """Test the extract_relevant_information function."""
    print("Testing extract_relevant_information...")
    sample_content = "Python is a high-level programming language. It is widely used for web development. " \
                     "Machine learning is a subset of artificial intelligence. Python is great for machine learning."
    keywords = ["Python", "programming"]
    relevant_sentences = extract_relevant_information(sample_content, keywords)
    print(f"  Found {len(relevant_sentences)} relevant sentences")
    for i, sentence in enumerate(relevant_sentences, 1):
        print(f"    {i}. {sentence}")
    return len(relevant_sentences) > 0

def test_search_web():
    """Test the search_web function."""
    print("\nTesting search_web...")
    try:
        urls = search_web("Python programming", num_results=2, engine="duckduckgo")
        print(f"  Found {len(urls)} URLs:")
        for i, url in enumerate(urls, 1):
            print(f"    {i}. {url}")
        return len(urls) > 0
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_scrape_webpage():
    """Test the scrape_webpage function."""
    print("\nTesting scrape_webpage...")
    try:
        page_data = scrape_webpage("https://httpbin.org/html")
        print(f"  Title: {page_data.get('title', 'N/A')}")
        print(f"  URL: {page_data.get('url', 'N/A')}")
        content_preview = page_data.get('content', 'N/A')[:100] + "..." if len(page_data.get('content', '')) > 100 else page_data.get('content', 'N/A')
        print(f"  Content preview: {content_preview}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_search_and_extract():
    """Test the search_and_extract function."""
    print("\nTesting search_and_extract...")
    try:
        results = search_and_extract("Python programming", ["Python", "programming"])
        print(f"  Found information from {len(results)} sources:")
        for i, result in enumerate(results[:2], 1):  # Limit to 2 results for brevity
            print(f"    {i}. Title: {result.get('title', 'N/A')}")
            print(f"       URL: {result.get('url', 'N/A')}")
            print(f"       Relevant sentences: {len(result.get('relevant_sentences', []))}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing search_utils.py functions")
    print("=" * 60)
    
    tests = [
        test_extract_relevant_information,
        test_search_web,
        test_scrape_webpage,
        test_search_and_extract
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}/{len(tests)}")
    print("=" * 60)

if __name__ == "__main__":
    main()