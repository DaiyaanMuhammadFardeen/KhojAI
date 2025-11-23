#!/bin/bash
# Quick restart script for demo

echo "Restarting KhojAI services for demo..."

# Kill any existing processes
pkill -f "java.*KhojAI"
pkill -f "node.*next"
pkill -f "ollama"

# Wait a moment
sleep 3

# Start backend (no security for demo)
echo "Starting backend..."
cd /home/daiyaan2002/Desktop/Projects/KhojAI
nohup ./mvnw spring-boot:run > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
sleep 15

# Start frontend
echo "Starting frontend..."
cd /home/daiyaan2002/Desktop/Projects/KhojAI/frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Start Ollama if needed
echo "Starting Ollama..."
nohup ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
echo "Ollama started with PID: $OLLAMA_PID"

echo ""
echo "Services started!"
echo "Access the application at http://localhost:3000"
echo "Backend API at http://localhost:8080"
echo "Ollama at http://localhost:11434"
echo ""
echo "Logs are available at:"
echo "- Backend: /tmp/backend.log"
echo "- Frontend: /tmp/frontend.log"
echo "- Ollama: /tmp/ollama.log"