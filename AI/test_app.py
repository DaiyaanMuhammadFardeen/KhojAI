#!/usr/bin/env python3
"""
Test cases for app.py to test the running WSGI server and verify
that POST requests with prompts return appropriate DuckDuckGo search results.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock
import asyncio
import time

# Add the AI directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import the app
from app import app
from fastapi.testclient import TestClient

class TestApp(unittest.TestCase):
    """Test cases for the FastAPI application endpoints."""

    def setUp(self):
        """Set up test client before each test method."""
        self.client = TestClient(app)

    def test_analyze_endpoint_success(self):
        """Test the /analyze endpoint with a simple prompt."""
        # Test data
        test_data = {
            "prompt": "What are the latest developments in artificial intelligence?",
            "include_search": False
        }

        # Make POST request
        response = self.client.post("/analyze", json=test_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the response contains expected fields
        self.assertIn("intents", data)
        self.assertIn("keywords", data)
        self.assertIn("search_queries", data)

    def test_analyze_endpoint_with_search_success(self):
        """Test the /analyze endpoint with search enabled."""
        # Test data
        test_data = {
            "prompt": "What are the latest developments in artificial intelligence?",
            "include_search": True
        }

        # Make POST request
        response = self.client.post("/analyze", json=test_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the response contains expected fields
        self.assertIn("intents", data)
        self.assertIn("keywords", data)
        self.assertIn("search_queries", data)
        self.assertIn("search_results", data)

    def test_analyze_endpoint_invalid_request(self):
        """Test the /analyze endpoint with invalid data."""
        # Test data with missing prompt
        test_data = {
            "include_search": True
        }

        # Make POST request
        response = self.client.post("/analyze", json=test_data)
        
        # Check response - should be a validation error
        self.assertEqual(response.status_code, 422)

    @patch('app.generate_response_with_web_search')
    def test_generate_response_endpoint_success(self, mock_generate):
        """Test the /generate-response endpoint with a mock response."""
        # Setup mock
        mock_response_text = "Based on recent developments, artificial intelligence has seen significant advances."
        mock_generate.return_value = mock_response_text
        
        # Test data
        test_data = {
            "prompt": "What are the latest developments in artificial intelligence?"
        }

        # Make POST request
        response = self.client.post("/generate-response", json=test_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the response contains expected message
        self.assertIn("message", data)
        self.assertEqual(data["message"], mock_response_text)
        
        # Verify the mock was called with correct argument
        mock_generate.assert_called_once_with(test_data["prompt"])

    @patch('app.generate_response_with_web_search')
    def test_generate_response_endpoint_exception(self, mock_generate):
        """Test the /generate-response endpoint when an exception occurs."""
        # Setup mock to raise exception
        mock_generate.side_effect = Exception("Test error")
        
        # Test data
        test_data = {
            "prompt": "What are the latest developments in artificial intelligence?"
        }

        # Make POST request
        response = self.client.post("/generate-response", json=test_data)
        
        # Check response - should be a 500 error
        self.assertEqual(response.status_code, 500)
        
        # Verify the mock was called
        mock_generate.assert_called_once_with(test_data["prompt"])

    def test_generate_response_endpoint_invalid_request(self):
        """Test the /generate-response endpoint with invalid data."""
        # Test data with missing prompt
        test_data = {}

        # Make POST request
        response = self.client.post("/generate-response", json=test_data)
        
        # Check response - should be a validation error
        self.assertEqual(response.status_code, 422)

    @patch('app.analyze_prompt')
    @patch('app.search_and_extract')
    def test_analyze_endpoint_integration(self, mock_search, mock_analyze):
        """Test the /analyze endpoint integration with mocked dependencies."""
        # Setup mocks
        mock_analyze.return_value = {
            "intents": ["question"],
            "keywords": [{"term": "artificial intelligence", "score": 0.9}],
            "search_queries": ["latest artificial intelligence developments"]
        }
        
        mock_search.return_value = [
            {
                "url": "https://example.com/ai-news",
                "title": "AI News Update",
                "relevant_sentences": [
                    "Recent breakthroughs in machine learning have been reported.",
                    "New AI models show improved performance."
                ]
            }
        ]
        
        # Test data
        test_data = {
            "prompt": "What are the latest developments in artificial intelligence?",
            "include_search": True
        }

        # Make POST request
        response = self.client.post("/analyze", json=test_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the response contains expected fields
        self.assertIn("intents", data)
        self.assertIn("keywords", data)
        self.assertIn("search_queries", data)
        self.assertIn("search_results", data)
        
        # Verify mocks were called
        mock_analyze.assert_called_once_with(test_data["prompt"], debug=False)
        self.assertEqual(mock_search.call_count, 1)

class TestAppWithLiveServer(unittest.TestCase):
    """Test cases that might require a live server (can be run separately)."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client before all tests."""
        cls.client = TestClient(app)
    
    def test_analyze_endpoint_live_search(self):
        """Test the /analyze endpoint with actual web search (if network available)."""
        # Test data
        test_data = {
            "prompt": "Latest Python programming news",
            "include_search": True
        }

        # Make POST request
        response = self.client.post("/analyze", json=test_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the response contains expected fields
        self.assertIn("intents", data)
        self.assertIn("keywords", data)
        self.assertIn("search_queries", data)
        self.assertIn("search_results", data)
        
        # Check that search results are returned (might be empty depending on search)
        self.assertIsInstance(data["search_results"], list)

    def test_generate_response_endpoint_live(self):
        """Test the /generate-response endpoint with actual processing."""
        # Test data
        test_data = {
            "prompt": "Latest developments in space exploration"
        }

        # Make POST request
        response = self.client.post("/generate-response", json=test_data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the response contains expected message
        self.assertIn("message", data)
        self.assertIsInstance(data["message"], str)
        self.assertGreater(len(data["message"]), 0)

def main():
    """Run the tests."""
    print("Running tests for app.py...")
    unittest.main(verbosity=2)

if __name__ == "__main__":
    main()