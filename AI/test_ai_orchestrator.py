#!/usr/bin/env python3
"""
Unit tests for ai_orchestrator.py
Focuses on testing the prompt construction for OLLAMA with web search results.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the AI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from ai_orchestrator import generate_response_with_web_search, build_context_from_information

class TestAIOrchestrator(unittest.TestCase):
    
    def setUp(self):
        """
        Set up test fixtures before each test method.
        """
        self.test_prompt = "What are the latest developments in quantum computing?"
        
        # Mock search results data
        self.mock_information = [
            {
                "url": "https://example.com/quantum1",
                "title": "Quantum Computing Advances in 2025",
                "relevant_sentences": [
                    "Scientists have made breakthrough progress in quantum error correction.",
                    "New quantum processors show increased stability and coherence times."
                ]
            },
            {
                "url": "https://example.com/quantum2", 
                "title": "Quantum Supremacy Update",
                "relevant_sentences": [
                    "Recent experiments have demonstrated quantum advantage in optimization problems.",
                    "Companies are investing heavily in quantum hardware development."
                ]
            }
        ]
    
    @patch('ai_orchestrator.analyze_prompt')
    @patch('ai_orchestrator.search_and_extract')
    @patch('ai_orchestrator.ollama.generate')
    def test_generate_response_with_web_search_success(self, mock_ollama, mock_search, mock_analyze):
        """
        Test successful generation of response with web search results.
        """
        # Setup mocks
        mock_analyze.return_value = {
            "intents": ["question"],
            "keywords": [{"term": "quantum computing", "score": 0.9}],
            "search_queries": ["quantum computing advances", "latest quantum computing news"]
        }
        
        mock_search.return_value = self.mock_information
        
        mock_ollama_response = {
            'response': 'Based on recent developments, quantum computing has seen significant advances in error correction and processor stability.'
        }
        mock_ollama.return_value = mock_ollama_response
        
        # Execute the function
        result = generate_response_with_web_search(self.test_prompt)
        
        # Assertions
        self.assertEqual(result, mock_ollama_response['response'])
        mock_analyze.assert_called_once_with(self.test_prompt)
        mock_search.assert_called()
        mock_ollama.assert_called_once()
        
        # Check that the prompt sent to OLLAMA contains the expected elements
        call_args = mock_ollama.call_args[1]  # Get kwargs from the call
        prompt_sent = call_args['prompt']
        
        # Verify that the prompt contains key elements
        self.assertIn("You are a helpful AI assistant", prompt_sent)
        self.assertIn(self.test_prompt, prompt_sent)
        self.assertIn("Quantum Computing Advances in 2025", prompt_sent)
        self.assertIn("Scientists have made breakthrough progress", prompt_sent)
        self.assertIn("Recent experiments have demonstrated quantum advantage", prompt_sent)
    
    @patch('ai_orchestrator.analyze_prompt')
    @patch('ai_orchestrator.search_and_extract')
    @patch('ai_orchestrator.ollama.generate')
    def test_generate_response_with_empty_search_results(self, mock_ollama, mock_search, mock_analyze):
        """
        Test generation of response when web search yields no results.
        """
        # Setup mocks
        mock_analyze.return_value = {
            "intents": ["question"],
            "keywords": [{"term": "quantum computing", "score": 0.9}],
            "search_queries": ["quantum computing advances"]
        }
        
        mock_search.return_value = []  # Empty search results
        
        mock_ollama_response = {
            'response': 'Quantum computing is an emerging field with potential for significant advances.'
        }
        mock_ollama.return_value = mock_ollama_response
        
        # Execute the function
        result = generate_response_with_web_search(self.test_prompt)
        
        # Assertions
        self.assertEqual(result, mock_ollama_response['response'])
        mock_analyze.assert_called_once_with(self.test_prompt)
        mock_search.assert_called_once()
        mock_ollama.assert_called_once()
    
    def test_build_context_from_information(self):
        """
        Test the build_context_from_information function directly.
        """
        # Execute the function
        context = build_context_from_information(self.mock_information)
        
        # Assertions
        self.assertIn("Quantum Computing Advances in 2025", context)
        self.assertIn("https://example.com/quantum1", context)
        self.assertIn("Scientists have made breakthrough progress", context)
        self.assertIn("Quantum Supremacy Update", context)
        self.assertIn("https://example.com/quantum2", context)
        self.assertIn("Recent experiments have demonstrated quantum advantage", context)
        # Check that sources are separated by ---
        self.assertIn("---", context)
    
    @patch('ai_orchestrator.analyze_prompt')
    @patch('ai_orchestrator.search_and_extract')
    @patch('ai_orchestrator.ollama.generate')
    def test_generate_response_with_ollama_error(self, mock_ollama, mock_search, mock_analyze):
        """
        Test handling of OLLAMA errors.
        """
        # Setup mocks
        mock_analyze.return_value = {
            "intents": ["question"],
            "keywords": [{"term": "quantum computing", "score": 0.9}],
            "search_queries": ["quantum computing advances"]
        }
        
        mock_search.return_value = self.mock_information
        
        # Simulate OLLAMA error
        mock_ollama.side_effect = Exception("Connection failed")
        
        # Execute the function
        result = generate_response_with_web_search(self.test_prompt)
        
        # Assertions
        self.assertTrue(isinstance(result, str))
        self.assertIn("Based on my search, here's what I found:", result)
        self.assertIn("Quantum Computing Advances in 2025", result)
    
    @patch('ai_orchestrator.analyze_prompt')
    @patch('ai_orchestrator.search_and_extract') 
    @patch('ai_orchestrator.ollama.generate')
    def test_generate_response_with_fallback_ollama_error(self, mock_ollama, mock_search, mock_analyze):
        """
        Test handling of OLLAMA errors in fallback response.
        """
        # Setup mocks
        mock_analyze.return_value = {
            "intents": ["question"],
            "keywords": [{"term": "quantum computing", "score": 0.9}],
            "search_queries": ["quantum computing advances"]
        }
        
        mock_search.return_value = []  # No search results
        
        # Simulate OLLAMA error in fallback
        mock_ollama.side_effect = Exception("Connection failed")
        
        # Execute the function
        result = generate_response_with_web_search(self.test_prompt)
        
        # Assertions
        self.assertTrue(isinstance(result, str))
        self.assertEqual(result, "I'm sorry, but I couldn't find relevant information to answer your query.")

if __name__ == '__main__':
    unittest.main()