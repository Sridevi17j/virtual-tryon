# Running Locally Without Docker

## Prerequisites
- Python 3.9+
- Node.js 18+
- Redis (optional)
- MinIO (optional)

## 1. Backend API Service

```bash
cd services/api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 2. ML Service

```bash
cd services/vton
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## 3. Frontend

```bash
cd frontend
npm install
npm start
```

## 4. Optional Services

### Redis (for job management)
```bash
# Install Redis
sudo apt update && sudo apt install redis-server
redis-server
```

### MinIO (for file storage)
```bash
# Download MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
./minio server ./data --console-address ":9001"
```

## Access Points

- Frontend: http://localhost:3000
- API: http://localhost:8000
- ML Service: http://localhost:8001
- MinIO Console: http://localhost:9001 (admin/password)

## Environment Variables

Create `.env` files in each service directory:

### services/api/.env
```
DEBUG=true
ML_SERVICE_URL=http://localhost:8001
REDIS_URL=redis://localhost:6379
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### services/vton/.env
```
DEBUG=true
MODEL_PATH=./models/viton-hd
```

### frontend/.env
```
REACT_APP_API_URL=http://localhost:8000
```