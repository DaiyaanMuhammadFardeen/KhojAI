#!/usr/bin/env python3
"""
Comprehensive test to verify the full web search pipeline is working
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from ai_orchestrator import generate_response_with_web_search
    
    # Test with the actual prompt
    prompt = "Tell me who is the chief advisor of bangladesh government after the July Revolution in 2024 is"
    
    print(f"Testing full pipeline for prompt: '{prompt}'")
    print("=" * 70)
    
    # This will test the entire pipeline:
    # 1. Intent detection
    # 2. Keyword extraction
    # 3. Search query generation
    # 4. Web search
    # 5. Information extraction
    response = generate_response_with_web_search(prompt)
    
    print("Generated response:")
    print("-" * 30)
    print(response)
    print("-" * 30)
    print("Test completed successfully!")
        
except Exception as e:
    print(f"Error during test: {e}")
    import traceback
    traceback.print_exc()