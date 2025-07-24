from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.api.routes import api_router
from app.services.storage import storage_service
from app.services.ml_client import ml_client

# Create directories
Path("uploads").mkdir(exist_ok=True)
Path("temp").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Virtual Try-On API Service...")
    
    # Initialize services
    try:
        await storage_service.initialize()
        await ml_client.initialize()
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down services...")
    await storage_service.cleanup()
    await ml_client.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Virtual Try-On API",
    description="API for virtual fashion try-on using VITON-HD",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Mount static files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Virtual Try-On API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check ML service
        ml_status = await ml_client.health_check()
        
        # Check storage service
        storage_status = await storage_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "ml_service": ml_status,
                "storage": storage_status
            },
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )