#!/usr/bin/env python3
# tests.py
# ------------------------------------------------------------
# Test suite for the LLM-powered prompt analyzer.
# ------------------------------------------------------------

import sys
import os
from typing import Dict, Any

# Add the current directory to the path so we can import prompt_analyzer_llm
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prompt_analyzer_llm import analyze_prompt
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Test cases covering various prompt types
TEST_CASES = [
    # Questions
    "What is the capital of France?",
    "Who invented the telephone?",
    "How does photosynthesis work?",
    
    # Commands
    "Calculate the square root of 144",
    "Summarize the latest AI research paper",
    "Translate 'Hello, how are you?' to French",
    
    # Creative requests
    "Write a short poem about autumn",
    "Generate a creative story about a robot learning to paint",
    
    # Code requests
    "Write a Python function to sort a list of dictionaries by a specific key",
    "How do I connect to a PostgreSQL database in Python?",
    
    # Translation requests
    "How do you say 'good morning' in Japanese?",
    "What is the German word for computer?",
    
    # Complex requests
    "Explain quantum computing in simple terms and give me some practical applications",
    "Find the best machine learning algorithm for image classification and explain why"
]

def validate_result(result: Dict[str, Any], test_case: str) -> bool:
    """Validate that the result conforms to expected structure and constraints."""
    print(Fore.CYAN + f"\nTesting: \"{test_case}\"" + Style.RESET_ALL)
    
    # Check that result is a dictionary
    assert isinstance(result, dict), "Result should be a dictionary"
    
    # Check required keys exist
    required_keys = ["intents", "keywords", "goals", "search_queries", "message"]
    for key in required_keys:
        assert key in result, f"Missing required key: {key}"
    
    # Check intents
    assert isinstance(result["intents"], list), "intents should be a list"
    assert len(result["intents"]) > 0, "intents should not be empty"
    print(Fore.GREEN + f"  ✓ Intents: {result['intents']}" + Style.RESET_ALL)
    
    # Check keywords
    assert isinstance(result["keywords"], list), "keywords should be a list"
    assert len(result["keywords"]) > 0, f"keywords should not be empty, got {len(result['keywords'])}"
    for kw in result["keywords"]:
        assert isinstance(kw, dict), "each keyword should be a dictionary"
        assert "term" in kw and "score" in kw, "each keyword should have 'term' and 'score'"
        assert isinstance(kw["term"], str), "keyword term should be a string"
        assert isinstance(kw["score"], (int, float)), "keyword score should be a number"
    print(Fore.GREEN + f"  ✓ Keywords: {len(result['keywords'])} items" + Style.RESET_ALL)
    
    # Check goals
    assert isinstance(result["goals"], list), "goals should be a list"
    assert len(result["goals"]) > 0, "goals should not be empty"
    for goal in result["goals"]:
        assert isinstance(goal, dict), "each goal should be a dictionary"
        assert "action" in goal and "object" in goal and "modifiers" in goal, "each goal should have 'action', 'object', and 'modifiers'"
        assert isinstance(goal["action"], str), "goal action should be a string"
        assert isinstance(goal["object"], str), "goal object should be a string"
        assert isinstance(goal["modifiers"], list), "goal modifiers should be a list"
    print(Fore.GREEN + f"  ✓ Goals: {len(result['goals'])} items" + Style.RESET_ALL)
    
    # Check search_queries
    assert isinstance(result["search_queries"], list), "search_queries should be a list"
    assert len(result["search_queries"]) > 0, f"search_queries should not be empty, got {len(result['search_queries'])}"
    for query in result["search_queries"]:
        assert isinstance(query, str), "each search query should be a string"
        assert len(query.strip()) > 0, "search queries should not be empty"
        assert len(query) < 200, "search queries should be reasonably short"
    print(Fore.GREEN + f"  ✓ Search Queries: {len(result['search_queries'])} items" + Style.RESET_ALL)
    
    # Check message
    assert isinstance(result["message"], str), "message should be a string"
    assert len(result["message"]) > 0, "message should not be empty"
    print(Fore.GREEN + f"  ✓ Message: {len(result['message'])} chars" + Style.RESET_ALL)
    
    # Check that the JSON is valid (by trying to serialize)
    import json
    try:
        json.dumps(result)
        print(Fore.GREEN + "  ✓ JSON serialization: Valid" + Style.RESET_ALL)
    except Exception as e:
        assert False, f"Result is not JSON serializable: {e}"
    
    return True

def run_tests():
    """Run all test cases and validate results."""
    print(Fore.YELLOW + "Running Prompt Analyzer Tests...\n" + Style.RESET_ALL)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        try:
            result = analyze_prompt(test_case, debug=False)
            validate_result(result, test_case)
            print(Fore.GREEN + f"Test {i}/{len(TEST_CASES)} PASSED\n" + Style.RESET_ALL)
            passed += 1
        except Exception as e:
            print(Fore.RED + f"Test {i}/{len(TEST_CASES)} FAILED: {e}\n" + Style.RESET_ALL)
            failed += 1
    
    print(Fore.YELLOW + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + Style.RESET_ALL)
    
    if failed > 0:
        sys.exit(1)
    else:
        print(Fore.GREEN + "All tests passed! ✅" + Style.RESET_ALL)

if __name__ == "__main__":
    run_tests()