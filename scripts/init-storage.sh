#!/bin/bash

set -e

echo "🗄️ Initializing MinIO storage..."

# Wait for MinIO to be ready
echo "Waiting for MinIO to start..."
until curl -f http://localhost:9000/minio/health/live 2>/dev/null; do
    echo "Waiting for MinIO..."
    sleep 2
done

# Install mc (MinIO Client) if not present
if ! command -v mc &> /dev/null; then
    echo "Installing MinIO client..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc
        chmod +x /usr/local/bin/mc
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install minio/stable/mc
    else
        echo "Please install MinIO client manually: https://docs.min.io/docs/minio-client-quickstart-guide.html"
        exit 1
    fi
fi

# Configure mc
echo "Configuring MinIO client..."
mc alias set local http://localhost:9000 minioadmin minioadmin

# Create buckets
echo "Creating storage buckets..."
mc mb local/virtual-tryon 2>/dev/null || echo "Bucket already exists"
mc mb local/uploads 2>/dev/null || echo "Bucket already exists"
mc mb local/results 2>/dev/null || echo "Bucket already exists"

# Set bucket policies
echo "Setting bucket policies..."
mc policy set public local/virtual-tryon
mc policy set public local/uploads
mc policy set public local/results

echo "✅ Storage initialization complete!"
echo ""
echo "MinIO Console: http://localhost:9001"
echo "Access Key: minioadmin"
echo "Secret Key: minioadmin"