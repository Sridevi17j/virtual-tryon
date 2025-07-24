#!/bin/bash

echo "🏥 Checking Virtual Try-On Services..."

check_service() {
    local name=$1
    local url=$2
    local port=$3
    
    if curl -s "$url" >/dev/null 2>&1; then
        echo "✅ $name - Running at $url"
    else
        if nc -z localhost $port 2>/dev/null; then
            echo "⚠️  $name - Port $port is open but service not responding"
        else
            echo "❌ $name - Not running (port $port)"
        fi
    fi
}

echo "📡 Service Status:"
check_service "Frontend" "http://localhost:3000" 3000
check_service "API" "http://localhost:8000/health" 8000
check_service "ML Service" "http://localhost:8001/health" 8001

echo ""
echo "🔍 Process Status:"
echo "Frontend processes:"
ps aux | grep -E "(http.server.*3000|npm.*start)" | grep -v grep | head -2

echo "Backend processes:"
ps aux | grep -E "(uvicorn.*800[01])" | grep -v grep | head -2

echo ""
echo "📋 Quick Tests:"
echo "Frontend: curl -s http://localhost:3000 | head -1"
echo "API:      curl -s http://localhost:8000/health"
echo "ML:       curl -s http://localhost:8001/health"