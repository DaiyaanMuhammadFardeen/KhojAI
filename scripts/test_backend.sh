#!/bin/bash
# Test backend accessibility

echo "Testing backend accessibility..."

# Test if backend is running on port 5000
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Backend is running on port 5000"
else
    echo "❌ Backend is not running on port 5000"
fi

# Test a simple public endpoint
echo "Testing public endpoint..."
curl -s -o /dev/null -w "HTTP Status Code: %{http_code}\n" http://localhost:5000/api/v1/auth/test

# Test CORS headers
echo "Testing CORS headers..."
curl -s -I -H "Origin: http://localhost:3000" http://localhost:5000/api/v1/auth/login | grep -i "access-control"

echo "Backend test complete."