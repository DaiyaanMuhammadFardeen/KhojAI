#!/usr/bin/env python3
"""
Integration test for the AI Orchestrator.
Tests the complete workflow including prompt analysis, web search, and response generation.
"""

import asyncio
import sys
import os

# Add the current directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_orchestrator import generate_response_with_web_search
from prompt_analyzer import analyze_prompt
from web_search import search_and_extract

async def test_prompt_analysis():
    """Test that prompt analysis works correctly."""
    print("=== Testing Prompt Analysis ===")
    
    test_prompts = [
        "What is the capital of France?",
        "Explain quantum computing",
        "Write a poem about spring"
    ]
    
    for prompt in test_prompts:
        print(f"\nTesting prompt: '{prompt}'")
        result = analyze_prompt(prompt)
        
        # Validate result structure
        assert "intents" in result, "Missing intents in analysis result"
        assert "keywords" in result, "Missing keywords in analysis result"
        assert "goals" in result, "Missing goals in analysis result"
        assert "search_queries" in result, "Missing search_queries in analysis result"
        
        print(f"  Intents: {result['intents']}")
        print(f"  Keywords: {[kw['term'] for kw in result['keywords'][:3]]}")
        print(f"  Search queries: {result['search_queries'][:2]}")
    
    print("✅ Prompt analysis tests passed\n")

async def test_web_search():
    """Test that web search and extraction works."""
    print("=== Testing Web Search and Extraction ===")
    
    query = "capital of France"
    keywords = ["capital", "France", "Paris"]
    
    print(f"Searching for: '{query}'")
    results = await search_and_extract(query, keywords)
    
    # Validate results
    assert isinstance(results, list), "Results should be a list"
    print(f"Found {len(results)} results")
    
    if results:
        result = results[0]
        assert "url" in result, "Result missing URL"
        assert "title" in result, "Result missing title"
        assert "relevant_sentences" in result, "Result missing relevant sentences"
        print(f"  Sample result: {result['title']}")
        print(f"  URL: {result['url']}")
        print(f"  Relevant sentences: {len(result['relevant_sentences'])}")
    
    print("✅ Web search tests passed\n")

async def test_full_orchestration():
    """Test the full AI orchestration workflow."""
    print("=== Testing Full AI Orchestration ===")
    
    test_prompts = [
        "What is the capital of France?",
        "Who invented the telephone?",
    ]
    
    for prompt in test_prompts:
        print(f"\nTesting full orchestration with: '{prompt}'")
        response = await generate_response_with_web_search(prompt)
        
        # Validate response
        assert isinstance(response, str), "Response should be a string"
        assert len(response) > 0, "Response should not be empty"
        
        print(f"  Generated response length: {len(response)} characters")
        print(f"  Sample: {response[:100]}...")
    
    print("✅ Full orchestration tests passed\n")

async def main():
    """Run all integration tests."""
    print("🤖 AI Orchestrator Integration Tests\n")
    
    try:
        await test_prompt_analysis()
        await test_web_search()
        await test_full_orchestration()
        
        print("🎉 All integration tests passed!")
        return 0
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)