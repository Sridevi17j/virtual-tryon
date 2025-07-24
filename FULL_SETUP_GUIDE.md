# 🚀 Complete Setup Guide - Frontend + Backend

## Quick Test Options

### Option 1: Frontend Only (Immediate)
```bash
# From project root
./run-frontend.sh

# Or open demo.html in browser
open demo.html
```

### Option 2: Full Stack (Frontend + Backend)
Follow the steps below for complete integration testing.

## Full Stack Setup

### Prerequisites
- Python 3.9+ 
- Node.js 18+
- (Optional) Docker Desktop
- (Optional) Redis
- (Optional) MinIO

### Step 1: Start Backend Services

#### 1A. Start API Service
```bash
# Terminal 1 - API Service
cd services/api

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DEBUG=true
export ML_SERVICE_URL=http://localhost:8001
export REDIS_URL=redis://localhost:6379

# Start API server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 1B. Start ML Service  
```bash
# Terminal 2 - ML Service
cd services/vton

# Install dependencies
pip install -r requirements.txt

# Set environment
export DEBUG=true
export MODEL_PATH=./models/viton-hd

# Start ML server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### 1C. Start Support Services (Optional)
```bash
# Terminal 3 - Redis (optional)
redis-server

# Terminal 4 - MinIO (optional)
mkdir -p data
minio server ./data --console-address ":9001"
```

### Step 2: Start Frontend

#### 2A. React Frontend
```bash
# Terminal 5 - React Frontend
cd frontend

# Install dependencies (if not done)
npm install --legacy-peer-deps

# Start development server
npm start
```

#### 2B. Alternative - Serve Build
```bash
# If npm start doesn't work
cd frontend
python3 -m http.server 3000 --directory build
```

## Testing the Full Stack

### 1. Check Service Health
```bash
# API Health
curl http://localhost:8000/health

# ML Service Health  
curl http://localhost:8001/health

# Frontend
open http://localhost:3000
```

### 2. Test API Endpoints
```bash
# Upload test file
curl -X POST -F "file=@test.jpg" http://localhost:8000/api/v1/upload

# Try virtual try-on
curl -X POST \
  -F "person_image=@person.jpg" \
  -F "garment_image=@shirt.jpg" \
  http://localhost:8000/api/v1/tryon
```

### 3. Test Full UI Flow
1. Open http://localhost:3000
2. Navigate to "Try On" page
3. Upload person and garment images
4. Click "Start Virtual Try-On"
5. See results (demo mode or real processing)

## Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | React UI |
| API | http://localhost:8000 | Backend API |
| ML Service | http://localhost:8001 | AI Processing |
| MinIO Console | http://localhost:9001 | File Storage UI |

## Troubleshooting

### Frontend Issues
```bash
# If React won't start
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
npm start

# Alternative: Use build
python3 -m http.server 3000 --directory build
```

### Backend Issues
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Install with pip
cd services/api
pip install --upgrade pip
pip install -r requirements.txt

# Test API directly
python3 -c "import fastapi; print('FastAPI ready')"
```

### ML Service Issues
```bash
# Install ML dependencies
cd services/vton
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Note: Will run in demo mode without VITON-HD models
```

## Docker Alternative (Easier)

If you have Docker installed:

```bash
# Build and start all services
make setup
make dev

# View logs
make logs

# Stop services
make stop
```

## API Testing with Postman/cURL

### Upload Image
```bash
curl -X POST \
  -F "file=@/path/to/image.jpg" \
  http://localhost:8000/api/v1/upload
```

### Virtual Try-On
```bash
curl -X POST \
  -F "person_image=@person.jpg" \
  -F "garment_image=@shirt.jpg" \
  http://localhost:8000/api/v1/tryon
```

### Check Job Status
```bash
curl http://localhost:8000/api/v1/jobs/JOB_ID
```

## Expected Behavior

### Demo Mode (Without Models)
- ✅ UI works perfectly
- ✅ File uploads work
- ✅ API responds
- ✅ Gets mock/demo results

### Full Mode (With Models)
- ✅ Real AI processing
- ✅ Actual virtual try-on results
- ✅ Higher quality outputs

## Success Indicators

✅ **Frontend**: Loads at localhost:3000  
✅ **API**: Returns JSON at localhost:8000/health  
✅ **ML**: Returns status at localhost:8001/health  
✅ **Integration**: Upload works, processing starts  
✅ **Results**: Demo results or real AI output displayed