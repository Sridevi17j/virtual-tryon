from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path
import asyncio
from typing import Optional
import tempfile
import shutil
from loguru import logger

from models.viton_model import VITONModel
from utils.image_processing import ImageProcessor
from utils.pose_estimation import PoseEstimator
from config import settings

app = FastAPI(title="VITON-HD ML Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
viton_model: Optional[VITONModel] = None
image_processor = ImageProcessor()
pose_estimator = PoseEstimator()

@app.on_event("startup")
async def startup_event():
    """Initialize the ML model on startup"""
    global viton_model
    logger.info("Starting VITON-HD ML Service...")
    
    try:
        viton_model = VITONModel(settings.MODEL_PATH)
        await viton_model.load_model()
        if viton_model.is_loaded:
            logger.info("VITON-HD model loaded successfully")
        else:
            logger.info("VITON-HD running in demo mode (model files not found)")
    except Exception as e:
        logger.error(f"Failed to initialize VITON-HD model: {e}")
        # Continue without model for development
        viton_model = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_status = "loaded" if viton_model and viton_model.is_loaded else "not_loaded"
    return {
        "status": "healthy",
        "model_status": model_status,
        "service": "viton-ml"
    }

@app.post("/try-on")
async def virtual_try_on(
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...)
):
    """
    Perform virtual try-on inference
    """
    # Continue even if model is not loaded - will use demo mode
    if not viton_model:
        raise HTTPException(status_code=503, detail="VITON model instance not available")
    
    # Validate file types
    if not person_image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Person file must be an image")
    
    if not garment_image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Garment file must be an image")
    
    try:
        # Create temporary directory for this request
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded files
            person_path = temp_path / f"person_{person_image.filename}"
            garment_path = temp_path / f"garment_{garment_image.filename}"
            result_path = temp_path / "result.jpg"
            
            # Write uploaded files to disk
            with open(person_path, "wb") as f:
                shutil.copyfileobj(person_image.file, f)
            
            with open(garment_path, "wb") as f:
                shutil.copyfileobj(garment_image.file, f)
            
            # Preprocess images
            logger.info("Preprocessing images...")
            processed_person = await image_processor.preprocess_person(person_path)
            processed_garment = await image_processor.preprocess_garment(garment_path)
            
            # Estimate pose
            logger.info("Estimating pose...")
            pose_data = await pose_estimator.estimate_pose(person_path)
            
            # Perform virtual try-on
            logger.info("Performing virtual try-on...")
            result_image = await viton_model.inference(
                processed_person, 
                processed_garment, 
                pose_data
            )
            
            # Save result
            await image_processor.save_result(result_image, result_path)
            
            # Return result image
            return FileResponse(
                result_path, 
                media_type="image/jpeg",
                filename="try_on_result.jpg"
            )
            
    except Exception as e:
        logger.error(f"Virtual try-on failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/preprocess")
async def preprocess_image(
    image: UploadFile = File(...),
    image_type: str = "person"  # person or garment
):
    """
    Preprocess image for virtual try-on
    """
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / f"input_{image.filename}"
            output_path = temp_path / f"processed_{image.filename}"
            
            # Save uploaded file
            with open(input_path, "wb") as f:
                shutil.copyfileobj(image.file, f)
            
            # Preprocess based on type
            if image_type == "person":
                processed_image = await image_processor.preprocess_person(input_path)
            elif image_type == "garment":
                processed_image = await image_processor.preprocess_garment(input_path)
            else:
                raise HTTPException(status_code=400, detail="Invalid image_type")
            
            # Save processed image
            await image_processor.save_result(processed_image, output_path)
            
            return FileResponse(
                output_path,
                media_type="image/jpeg",
                filename=f"processed_{image.filename}"
            )
            
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)