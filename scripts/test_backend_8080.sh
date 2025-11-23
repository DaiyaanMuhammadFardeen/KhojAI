#!/bin/bash
# Test backend accessibility on port 8080

echo "Testing backend accessibility on port 8080..."

# Test if backend is running on port 8080
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Backend is running on port 8080"
else
    echo "❌ Backend is not running on port 8080"
fi

# Test a simple public endpoint if the backend is running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "Testing public endpoints..."
    
    # Test auth endpoint
    echo "Testing /api/v1/auth/login endpoint..."
    curl -s -o /dev/null -w "HTTP Status Code: %{http_code}\n" \
         -H "Content-Type: application/json" \
         -d '{"username":"test","password":"test"}' \
         http://localhost:8080/api/v1/auth/login
    
    # Test CORS headers
    echo "Testing CORS headers..."
    curl -s -I -H "Origin: http://localhost:3000" http://localhost:8080/api/v1/auth/login | grep -i "access-control"
else
    echo "Skipping endpoint tests since backend is not running"
fi

echo "Backend test complete."