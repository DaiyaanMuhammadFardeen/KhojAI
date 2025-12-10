#!/usr/bin/env python3
"""
Test script for the optimized patterns.py
"""

from prompt_analyzer import analyze_prompt

def test_patterns():
    test_cases = [
        "What is the weather today?",
        "How does photosynthesis work?",
        "Search for Python tutorials",
        "Find the best restaurants in New York",
        "Compare iPhone 14 and Samsung Galaxy S23",
        "Explain quantum computing",
        "Write a story about space exploration",
        "Calculate the area of a circle",
        "Recommend a good book to read",
        "Define artificial intelligence",
        "Show me how to code in Python",
        "Is climate change real?",
        "Look up the population of Tokyo",
        "Tell me about ancient Rome",
        "What's the difference between Python and Java?",
        "Suggest some healthy dinner recipes",
        "Process this data and generate a report",
        "Verify if this information is correct"
    ]
    
    print("Testing optimized patterns...\n")
    
    for i, prompt in enumerate(test_cases, 1):
        print(f"{i:2d}. Prompt: '{prompt}'")
        result = analyze_prompt(prompt)
        intents = result["intents"]
        keywords = result["keywords"][:5]  # Top 5 keywords
        
        print(f"     Intents: {intents}")
        print(f"     Keywords: {[kw['term'] for kw in keywords]}")
        print()

if __name__ == "__main__":
    test_patterns()