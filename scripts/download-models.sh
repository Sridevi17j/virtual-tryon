#!/bin/bash

set -e

echo "📥 Downloading VITON-HD models..."

# Create models directory
mkdir -p models/viton-hd

# Check if models already exist
if [ -d "models/viton-hd/checkpoints" ]; then
    echo "✅ Models already exist. Skipping download."
    exit 0
fi

# Download VITON-HD models
echo "Downloading VITON-HD checkpoints..."
cd models/viton-hd

# Method 1: Download from official repository (if available)
if command -v git &> /dev/null; then
    echo "Cloning VITON-HD repository..."
    git clone https://github.com/shadow2496/VITON-HD.git temp_repo
    
    # Check if checkpoints exist in repo
    if [ -d "temp_repo/checkpoints" ]; then
        mv temp_repo/checkpoints ./
        echo "✅ Checkpoints found in repository"
    fi
    
    # Clean up
    rm -rf temp_repo
fi

# Method 2: Download pre-trained models from Google Drive or other sources
# Note: You'll need to provide actual download links
echo "📝 Note: Please manually download VITON-HD pre-trained models:"
echo "1. Download from: https://drive.google.com/drive/folders/0Bw6m_66JSYLlTXdnUGFNd2ZMRHM"
echo "2. Extract to: ./models/viton-hd/checkpoints/"
echo ""
echo "Expected structure:"
echo "models/viton-hd/"
echo "├── checkpoints/"
echo "│   ├── gen_model_000200.pt"
echo "│   ├── dis_model_000200.pt"
echo "│   └── ..."

# Create placeholder structure
mkdir -p checkpoints
echo "# VITON-HD Models" > checkpoints/README.md
echo "Download pre-trained models and place them in this directory." >> checkpoints/README.md

cd ../..

echo "⚠️  Manual download required for VITON-HD models."
echo "See instructions in models/viton-hd/checkpoints/README.md"