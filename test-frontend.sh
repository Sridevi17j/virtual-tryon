#!/bin/bash

echo "🧪 Testing Virtual Try-On Frontend..."

cd frontend

echo "📦 Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "🔨 Testing build process..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📁 Build output:"
    ls -la build/
    echo ""
    echo "🌐 To run the app:"
    echo "  npm start  (development server)"
    echo "  serve -s build  (serve production build)"
    echo ""
    echo "🚀 Frontend is ready to run!"
else
    echo "❌ Build failed!"
    exit 1
fi