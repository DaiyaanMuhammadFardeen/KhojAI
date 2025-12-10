#!/bin/bash

# Script to start all KhojAI services asynchronously
# Services: Ollama, Spring Boot Backend, Next.js Frontend

echo "Starting all KhojAI services..."

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on a port
kill_port() {
    local port=$1
    local pid=$(lsof -t -i:$port)
    if [ ! -z "$pid" ]; then
        echo "Killing process on port $port (PID: $pid)"
        kill $pid
        sleep 2
    fi
}

# Kill any existing processes on our ports
echo "Checking for processes on required ports..."
check_port 11434 && kill_port 11434  # Ollama
check_port 8080 && kill_port 8080  # Spring Boot Backend
check_port 3000 && kill_port 3000  # Next.js Frontend

# Start Ollama
echo "Starting Ollama..."
nohup ollama serve > /tmp/ollama.log 2>&1 &
OLLAMA_PID=$!
disown
echo "Ollama started with PID: $OLLAMA_PID"

# Wait for Ollama to start
sleep 5

# Pull a default model for Ollama (if not already present)
echo "Checking for Ollama models..."
if ! ollama list | grep -q "llama3"; then
    echo "Pulling llama3 model..."
    nohup ollama pull llama3 > /tmp/ollama_pull.log 2>&1 &
    disown
fi

# Start Spring Boot Backend
echo "Starting Spring Boot Backend..."
cd /home/daiyaan2002/Desktop/Projects/KhojAI
nohup ./mvnw spring-boot:run > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
disown
echo "Spring Boot Backend started with PID: $BACKEND_PID"

# Wait a bit for backend to start
sleep 10

# Start Next.js Frontend
echo "Starting Next.js Frontend..."
cd /home/daiyaan2002/Desktop/Projects/KhojAI/frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
disown
echo "Next.js Frontend started with PID: $FRONTEND_PID"

echo ""
echo "All services started!"
echo "Ollama PID: $OLLAMA_PID"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Access the application at http://localhost:3000"
echo "Backend API at http://localhost:5000"
echo "Ollama at http://localhost:11434"
echo ""
echo "Logs are available at:"
echo "- Ollama: /tmp/ollama.log"
echo "- Backend: /tmp/backend.log"
echo "- Frontend: /tmp/frontend.log"
echo ""
echo "To stop all services, run: ./stop.sh"