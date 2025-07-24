#!/bin/bash

echo "🤖 Starting VITON-HD Service..."
echo "📋 Setting up Python environment..."

cd services/vton

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing VITON dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p temp
mkdir -p ../../models/viton-hd/checkpoints

echo ""
echo "🚀 Starting VITON-HD Service on port 8002..."
echo "⚠️  Note: VITON models not found - will run in demo mode"
echo "   For full functionality, download VITON-HD model weights to models/viton-hd/checkpoints/"
echo ""

python main.py