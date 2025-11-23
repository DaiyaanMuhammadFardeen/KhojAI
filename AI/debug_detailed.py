#!/usr/bin/env python3
"""
Detailed debug script to trace each step of the search and extraction process
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from search_utils import search_web, scrape_webpage, extract_relevant_information
    
    # Test with a simple query
    query = "Bangladesh chief advisor July 2024"
    keywords = ["chief advisor", "Bangladesh", "July Revolution"]
    
    print(f"Debugging search process for query: '{query}'")
    print("=" * 70)
    
    # Step 1: Search the web
    print("Step 1: Searching web...")
    urls = search_web(query, num_results=2)
    print(f"Found {len(urls)} URLs:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    
    if not urls:
        print("No URLs found. Exiting.")
        sys.exit(1)
    
    # Step 2: Scrape the first URL
    url = urls[0]
    print(f"\nStep 2: Scraping content from {url}")
    page_data = scrape_webpage(url)
    
    print(f"Page data keys: {list(page_data.keys())}")
    print(f"Title: {page_data.get('title', 'N/A')}")
    content = page_data.get('content', '')
    print(f"Content length: {len(content)}")
    print(f"Content preview: {content[:200]}...")
    
    # Check for failure conditions
    if "Failed" in content:
        print("Content scraping failed!")
        print(f"Error: {content}")
    elif "Blocked" in content:
        print("Content blocked by robots.txt")
    elif len(content) < 100:
        print("Content too short")
    else:
        print("Content successfully scraped")
    
    # Step 3: Extract relevant information
    print(f"\nStep 3: Extracting relevant information with keywords: {keywords}")
    relevant_info = extract_relevant_information(content, keywords)
    print(f"Found {len(relevant_info)} relevant sentences")
    
    for i, sentence in enumerate(relevant_info[:5], 1):
        print(f"  {i}. {sentence}")
        
    if not relevant_info:
        print("No relevant information found. Let's check why:")
        print("Keywords in lowercase:", [k.lower() for k in keywords])
        # Check if any keywords appear in content
        content_lower = content.lower()
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in content_lower:
                print(f"Keyword '{kw}' found in content")
            else:
                print(f"Keyword '{kw}' NOT found in content")
        
except Exception as e:
    print(f"Error during debug: {e}")
    import traceback
    traceback.print_exc()