#!/bin/bash

set -e

echo "🚀 Setting up Virtual Try-On Fashion App..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p models uploads logs

# Create environment files if they don't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# ML Service Configuration
VTON_HOST=0.0.0.0
VTON_PORT=8001

# Storage Configuration
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=virtual-tryon

# Redis Configuration
REDIS_URL=redis://redis:6379

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
EOF
fi

# Make scripts executable
echo "🔧 Setting permissions..."
chmod +x scripts/*.sh

# Pull base images
echo "📥 Pulling base Docker images..."
docker pull node:18-alpine
docker pull python:3.9-slim
docker pull redis:7-alpine
docker pull minio/minio:latest
docker pull nginx:alpine

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run 'make install-models' to download VITON-HD models"
echo "2. Run 'make dev' to start development environment"
echo "3. Open http://localhost:3000 in your browser"