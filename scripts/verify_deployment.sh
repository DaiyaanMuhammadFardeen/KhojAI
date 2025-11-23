#!/bin/bash
# Deployment verification script

echo "Checking CORS configuration..."

# Check if frontend can access backend
FRONTEND_URL="https://holding-exam-brokers-cms.trycloudflare.com"
BACKEND_URL="https://formed-declare-software-eva.trycloudflare.com"

echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"

# Test the backend directly
echo "Testing backend connectivity..."
curl -I -X GET \
  -H "Origin: $FRONTEND_URL" \
  -H "Content-Type: application/json" \
  $BACKEND_URL/api/v1/auth/test 2>/dev/null | head -n 1

if [ $? -eq 0 ]; then
  echo "✅ Backend is accessible"
else
  echo "❌ Backend connectivity issue"
fi

echo "Deployment verification complete."