#!/bin/bash

echo "🚀 Starting Enhanced ML Service with API Fallbacks..."
echo "📋 Setting up Python environment..."

# We're already in the ml-service-enhanced directory

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing enhanced ML dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p temp results

echo ""
echo "🤖 Starting Enhanced ML Service on port 8001..."
echo "✨ Features:"
echo "   - Multi-API fallback (Replicate, HuggingFace)"
echo "   - Enhanced demo processing with color matching"
echo "   - Smart garment positioning"
echo "   - Soft edge blending"
echo ""

python main.py