#!/bin/bash

echo "🚀 Starting Virtual Try-On React Frontend..."

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

cd frontend

echo "📋 Starting React app..."

# Check if build directory exists
if [ -d "build" ] && [ -f "build/index.html" ]; then
    echo "✅ Found React build, starting server..."
    
    # Find available port
    PORT=3001
    while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
        PORT=$((PORT + 1))
    done
    
    echo "🌐 React Frontend available at: http://localhost:$PORT"
    echo "📱 Demo comparison at: http://localhost:$PORT/../demo.html"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    python3 -m http.server $PORT --directory build
else
    echo "❌ No React build found"
    echo ""
    echo "The React build is missing. Please check the setup."
    echo "You can use the demo.html file instead:"
    echo "  open ../demo.html"
    exit 1
fi