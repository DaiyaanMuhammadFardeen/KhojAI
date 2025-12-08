#!/bin/bash

echo "🚀 Real-time Streaming Test"
echo "========================="
echo "Sending request to backend service..."
echo ""

# Use curl with unbuffered output to show streaming data in real-time
curl -N -X POST http://localhost:8080/api/v1/ai/stream-search \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the latest developments in quantum computing?"}' \
  --no-buffer

echo ""
echo ""
echo "✅ Streaming test completed!"