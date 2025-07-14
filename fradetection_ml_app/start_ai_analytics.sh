#!/bin/bash

echo "🚀 Starting AI Analytics System..."

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use"
        return 1
    else
        echo "Port $1 is available"
        return 0
    fi
}

# Check if required ports are available
echo "Checking ports..."
check_port 3004 || { echo "❌ Port 3004 (Prostgles) is already in use"; exit 1; }
check_port 8000 || { echo "❌ Port 8000 (FastAPI) is already in use"; exit 1; }
check_port 5432 || { echo "❌ Port 5432 (PostgreSQL) is not running. Please start PostgreSQL first."; exit 1; }

echo "✅ All ports are available"

# Start PostgreSQL if not running (optional - uncomment if needed)
# echo "Starting PostgreSQL..."
# docker-compose -f backend_mlaas/docker-compose.yml up -d postgres

# Install FastAPI dependencies
echo "📦 Installing FastAPI dependencies..."
cd fastapi_middleware
pip install -r requirements.txt
cd ..

# Start FastAPI backend in background
echo "🔧 Starting FastAPI AI Analytics Backend..."
cd fastapi_middleware
python api/main.py &
FASTAPI_PID=$!
cd ..

# Wait a moment for FastAPI to start
sleep 3

# Start Prostgles frontend
echo "🌐 Starting Prostgles Frontend..."
cd frontend/prostgles
./start.sh &
PROSTGLES_PID=$!
cd ../..

echo "✅ AI Analytics System is starting..."
echo "📊 Frontend: http://localhost:3004"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🎯 Navigate to http://localhost:3004/ai-analytics to use the AI Analytics Dashboard"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $FASTAPI_PID 2>/dev/null
    kill $PROSTGLES_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait 