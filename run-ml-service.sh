#!/bin/bash

echo "🤖 Starting ML Service for Virtual Try-On..."

# Check if we're in the right directory
if [ ! -d "ml-service" ]; then
    echo "❌ Please run this script from the project root directory"
    echo "Expected to find ml-service directory"
    exit 1
fi

cd ml-service

echo "📋 Setting up Python environment for ML service..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing ML dependencies..."
pip install -r requirements.txt

echo "🧠 Starting ML service..."
echo "ML Service will be available at: http://localhost:8001"
echo "ML API docs will be available at: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the ML service"

python main.py