#!/bin/bash

echo "🚀 Starting Next.js Frontend..."

# Check if we're in the right directory
if [ ! -d "nextjs-frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    echo "Expected to find nextjs-frontend directory"
    exit 1
fi

cd nextjs-frontend

echo "📋 Installing dependencies..."
npm install

echo "🌐 Starting development server..."
echo "Frontend will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"

npm run dev