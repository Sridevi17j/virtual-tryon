#!/bin/bash

echo "=€ Starting Python Backend..."

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "L Please run this script from the project root directory"
    echo "Expected to find backend directory"
    exit 1
fi

cd backend

echo "=Ë Setting up Python environment..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "< Starting backend server..."
echo "Backend will be available at: http://localhost:8000"
echo "API docs will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

python main.py