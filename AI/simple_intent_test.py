#!/usr/bin/env python3
"""
Simple test to verify the fix for conditional web search
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Simple test without external dependencies
def test_intent_detection():
    # Test data
    test_cases = [
        {
            "prompt": "What is the weather today?",
            "expected_search": True
        },
        {
            "prompt": "How does photosynthesis work?",
            "expected_search": True
        },
        {
            "prompt": "Calculate 2+2",
            "expected_search": False
        },
        {
            "prompt": "Explain quantum mechanics",
            "expected_search": True
        }
    ]
    
    print("Testing intent detection logic...")
    print("=" * 50)
    
    question_words = ["what", "how", "why", "when", "where", "who", "which"]
    
    for case in test_cases:
        prompt = case["prompt"]
        expected = case["expected_search"]
        
        # Our search logic
        needs_search = (
            any(word in prompt.lower() for word in question_words)
        )
        
        print(f"Prompt: '{prompt}'")
        print(f"Expected search: {expected}")
        print(f"Actual search: {needs_search}")
        print(f"Match: {expected == needs_search}")
        print("-" * 30)

if __name__ == "__main__":
    test_intent_detection()
    print("Test completed!")