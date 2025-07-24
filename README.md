# Virtual Try-On Fashion App

A Virtual Try-On Fashion App where users upload their photo and garment images to see realistic previews of how clothing fits on their body.

## Architecture

- **Frontend**: Next.js with TypeScript and Tailwind CSS
- **Backend**: FastAPI Python service with simple file handling
- **Standalone Services**: No Docker required - run each service separately

## Quick Start

### Option 1: Run All Services (Recommended)

```bash
# Terminal 1: Start ML Service
./run-ml-service.sh

# Terminal 2: Start Backend  
./run-backend.sh

# Terminal 3: Start Frontend
./run-frontend.sh
```

### Option 2: Run Without ML Service (Fallback Mode)

```bash
# Terminal 1: Start Backend
./run-backend.sh

# Terminal 2: Start Frontend
./run-frontend.sh
```

### Option 3: Manual Setup

**ML Service:**
```bash
cd ml-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd nextjs-frontend
npm install
npm run dev
```

## Services

- **Frontend**: http://localhost:3000 (Next.js)
- **Backend**: http://localhost:8000 (FastAPI)
- **ML Service**: http://localhost:8001 (ML Processing)
- **API Docs**: http://localhost:8000/docs (Main API)
- **ML API Docs**: http://localhost:8001/docs (ML API)

## Project Structure

```
Virtual Costume/
├── nextjs-frontend/          # Next.js frontend application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # React components
│   │   └── ...
│   └── package.json
├── backend/                 # Main FastAPI backend
│   ├── main.py             # Main API service
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # File upload directory
├── ml-service/             # ML Processing service
│   ├── main.py             # Advanced ML processing
│   ├── requirements.txt    # ML dependencies
│   └── results/            # ML processing results
├── run-frontend.sh         # Frontend startup script
├── run-backend.sh          # Backend startup script
└── run-ml-service.sh       # ML service startup script
```

## Features

- 🎨 Modern Next.js frontend with TypeScript  
- ⚡ FastAPI backend with automatic API docs
- 🧠 **Separate ML service with advanced image processing**
- 📁 File upload and processing pipeline
- 🎯 **Smart fallback system** (ML → Demo → Error handling)
- 📱 Responsive design with Tailwind CSS
- 🔄 Real-time job status tracking
- 🖼️ **Enhanced virtual try-on** with better blending and effects

## How It Works

1. **Frontend** uploads images to **Main Backend**
2. **Main Backend** tries to call **ML Service** for advanced processing
3. **ML Service** performs sophisticated image blending with:
   - Intelligent garment positioning
   - Soft edge blending with masks
   - Color temperature matching
   - Sharpening and post-processing effects
4. If **ML Service** fails, falls back to simple demo processing
5. **Frontend** displays the result image

## Development Notes

- **ML Service**: More sophisticated image processing than basic overlay
- **Fallback System**: Ensures the app always works even if ML service is down
- **Microservices**: Clean separation between API logic and ML processing
- **Production Ready**: Easy to replace ML service with actual VITON-HD models