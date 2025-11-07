#!/usr/bin/env python3
"""
Simple test for the optimized patterns
"""

from prompt_analyzer import analyze_prompt

# Test cases
test_prompts = [
    "What is machine learning?",
    "Search for Python tutorials",
    "How does photosynthesis work?",
    "Compare iPhone 14 and Samsung Galaxy S23",
    "Write a story about space exploration"
]

print("Testing optimized intent patterns:\n")

for prompt in test_prompts:
    result = analyze_prompt(prompt)
    print(f"Prompt: '{prompt}'")
    print(f"Intents: {result['intents']}")
    print(f"Top keywords: {[kw['term'] for kw in result['keywords'][:3]]}")
    print("-" * 50)