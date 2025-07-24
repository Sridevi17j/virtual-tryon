#!/bin/bash

echo "🚀 Starting Virtual Try-On Full Stack..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Create tmux session for multiple terminals
if command_exists tmux; then
    echo "🖥️  Starting services in tmux session..."
    
    # Create new session
    tmux new-session -d -s virtual-tryon
    
    # API Service
    tmux new-window -t virtual-tryon:1 -n 'API'
    tmux send-keys -t virtual-tryon:1 'cd services/api && pip install -r requirements.txt 2>/dev/null && export DEBUG=true && export ML_SERVICE_URL=http://localhost:8001 && uvicorn main:app --host 0.0.0.0 --port 8000 --reload' C-m
    
    # ML Service
    tmux new-window -t virtual-tryon:2 -n 'ML'
    tmux send-keys -t virtual-tryon:2 'cd services/vton && pip install -r requirements.txt 2>/dev/null && export DEBUG=true && uvicorn main:app --host 0.0.0.0 --port 8001 --reload' C-m
    
    # Frontend
    tmux new-window -t virtual-tryon:3 -n 'Frontend'
    tmux send-keys -t virtual-tryon:3 'cd frontend && python3 -m http.server 3000 --directory build 2>/dev/null || npm start' C-m
    
    echo "✅ Services starting in tmux session 'virtual-tryon'"
    echo ""
    echo "📱 Access points:"
    echo "   Frontend:  http://localhost:3000"
    echo "   API:       http://localhost:8000"
    echo "   ML:        http://localhost:8001"
    echo ""
    echo "🖥️  View services: tmux attach -t virtual-tryon"
    echo "🛑 Stop all: tmux kill-session -t virtual-tryon"
    echo ""
    echo "Waiting 10 seconds for services to start..."
    sleep 10
    
    # Open browser
    if command_exists xdg-open; then
        xdg-open http://localhost:3000
    elif command_exists open; then
        open http://localhost:3000
    else
        echo "🌐 Open http://localhost:3000 in your browser"
    fi
    
else
    echo "⚠️  tmux not found. Starting services manually..."
    echo ""
    echo "Please run these commands in separate terminals:"
    echo ""
    echo "Terminal 1 (API):"
    echo "cd services/api && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    echo "Terminal 2 (ML):"
    echo "cd services/vton && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
    echo ""
    echo "Terminal 3 (Frontend):"
    echo "cd frontend && npm start"
    echo ""
    echo "Then open: http://localhost:3000"
fi