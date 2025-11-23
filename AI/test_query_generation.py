#!/usr/bin/env python3
"""
Test script to analyze search queries for the Bangladesh question
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import the analyzer
try:
    from prompt_analyzer import analyze_prompt
    
    # Test with the actual prompt
    prompt = "Tell me who is the chief advisor of bangladesh government after the July Revolution in 2024 is"
    
    print("Analyzing prompt:", prompt)
    print("=" * 60)
    
    result = analyze_prompt(prompt)
    
    print("Intents detected:", result.get("intents", []))
    print("Keywords extracted:", [k["term"] for k in result.get("keywords", [])])
    print("Search queries generated:", result.get("search_queries", []))
    print("=" * 60)
    
    # Test the search queries individually
    print("Testing search queries:")
    for i, query in enumerate(result.get("search_queries", [])):
        print(f"{i+1}. '{query}'")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()