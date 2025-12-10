#!/bin/bash

# Script to stop all KhojAI services

echo "Stopping all KhojAI services..."

# Function to kill process by PID
kill_pid() {
    local pid=$1
    local name=$2
    if [ ! -z "$pid" ] && kill -0 $pid 2>/dev/null; then
        echo "Stopping $name (PID: $pid)"
        kill $pid
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "Force killing $name (PID: $pid)"
            kill -9 $pid
        fi
    else
        echo "$name is not running"
    fi
}

# Read PIDs from the run script log or process list
echo "Finding service processes..."

# Kill frontend (port 3000)
FRONTEND_PID=$(lsof -t -i:3000)
kill_pid $FRONTEND_PID "Frontend"

# Kill backend (port 5000 - changed from 8080)
BACKEND_PID=$(lsof -t -i:8080)
kill_pid $BACKEND_PID "Backend"

# Kill Ollama (port 11434)
OLLAMA_PID=$(lsof -t -i:11434)
kill_pid $OLLAMA_PID "Ollama"

# Also try to kill any remaining Node.js, Java, or Python processes that might be from our services
echo "Checking for any remaining service processes..."

# Kill any remaining node processes
NODE_PIDS=$(pgrep -f "node.*next")
if [ ! -z "$NODE_PIDS" ]; then
    echo "Killing remaining Node.js processes: $NODE_PIDS"
    kill $NODE_PIDS 2>/dev/null
fi

# Kill any remaining Java processes (Spring Boot)
JAVA_PIDS=$(pgrep -f "java.*spring")
if [ ! -z "$JAVA_PIDS" ]; then
    echo "Killing remaining Java processes: $JAVA_PIDS"
    kill $JAVA_PIDS 2>/dev/null
fi

# Kill any remaining Ollama processes
OLAMA_PIDS=$(pgrep -f "ollama")
if [ ! -z "$OLAMA_PIDS" ]; then
    echo "Killing remaining Ollama processes: $OLAMA_PIDS"
    kill $OLAMA_PIDS 2>/dev/null
fi

echo "All services stopped!"