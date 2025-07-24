"""
Real VITON-HD Virtual Try-On Service
Implements actual virtual try-on using VITON-HD model with pose estimation and human parsing
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import uuid
import os
import asyncio
import time
from pathlib import Path
from typing import Optional, Dict, List
import json

# Import our VITON modules
from viton_pipeline import VITONPipeline
from pose_estimator import PoseEstimator
from human_parser import HumanParser
from utils import setup_logging, download_models

# Setup
Path("temp").mkdir(exist_ok=True)
Path("results").mkdir(exist_ok=True)
Path("models").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

app = FastAPI(
    title="Real VITON-HD Service",
    description="Production-ready Virtual Try-On using VITON-HD with pose estimation",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/results", StaticFiles(directory="results"), name="results")
app.mount("/temp", StaticFiles(directory="temp"), name="temp")

# Global pipeline instances
viton_pipeline: Optional[VITONPipeline] = None
pose_estimator: Optional[PoseEstimator] = None  
human_parser: Optional[HumanParser] = None

# Job tracking
processing_jobs: Dict[str, Dict] = {}

class VITONRequest(BaseModel):
    job_id: str
    category: str = "upper_body"  # upper_body, lower_body, dress
    preserve_background: bool = True
    high_quality: bool = True

class VITONResponse(BaseModel):
    job_id: str
    status: str
    result_url: Optional[str] = None
    pose_keypoints: Optional[List] = None
    segmentation_mask: Optional[str] = None
    processing_time: Optional[float] = None
    message: Optional[str] = None
    model_info: Optional[Dict] = None

@app.on_event("startup")
async def startup_event():
    """Initialize VITON models on startup"""
    global viton_pipeline, pose_estimator, human_parser
    
    setup_logging()
    
    try:
        print("🚀 Initializing Real VITON-HD Service...")
        
        # Download models if needed
        print("📥 Checking/downloading models...")
        await download_models()
        
        # Initialize pose estimator
        print("🕺 Loading pose estimation model...")
        pose_estimator = PoseEstimator()
        
        # Initialize human parser  
        print("👤 Loading human parsing model...")
        human_parser = HumanParser()
        
        # Initialize VITON pipeline
        print("👗 Loading VITON-HD model...")
        viton_pipeline = VITONPipeline()
        
        print("✅ All models loaded successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize models: {e}")
        raise e

@app.get("/")
async def root():
    return {
        "service": "Real VITON-HD Virtual Try-On",
        "version": "2.0.0",
        "status": "running",
        "models": {
            "viton": "VITON-HD",
            "pose": "MediaPipe/OpenPose",
            "parser": "Human Parsing Network"
        },
        "capabilities": [
            "pose-aware-synthesis",
            "human-parsing", 
            "clothing-segmentation",
            "realistic-warping",
            "lighting-adaptation"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    global viton_pipeline, pose_estimator, human_parser
    
    models_ready = all([
        viton_pipeline is not None,
        pose_estimator is not None, 
        human_parser is not None
    ])
    
    return {
        "status": "healthy" if models_ready else "initializing",
        "models_loaded": models_ready,
        "gpu_available": viton_pipeline.gpu_available if viton_pipeline else False,
        "active_jobs": len(processing_jobs),
        "service": "real-viton-hd"
    }

@app.get("/models")
async def list_models():
    """List available models and their status"""
    global viton_pipeline, pose_estimator, human_parser
    
    return {
        "viton_hd": {
            "loaded": viton_pipeline is not None,
            "version": "VITON-HD-512",
            "description": "High-resolution virtual try-on with pose awareness"
        },
        "pose_estimator": {
            "loaded": pose_estimator is not None,
            "version": "MediaPipe-v0.10",
            "description": "Real-time pose detection with 33 landmarks"
        },
        "human_parser": {
            "loaded": human_parser is not None,
            "version": "ATR-ResNet",
            "description": "Human parsing for clothing segmentation"
        }
    }

async def process_viton_real(
    person_image_path: str,
    garment_image_path: str, 
    job_id: str,
    category: str = "upper_body",
    preserve_background: bool = True,
    high_quality: bool = True
) -> VITONResponse:
    """Real VITON-HD processing pipeline"""
    
    start_time = time.time()
    
    try:
        global viton_pipeline, pose_estimator, human_parser
        
        if not all([viton_pipeline, pose_estimator, human_parser]):
            raise Exception("Models not properly initialized")
        
        print(f"🎬 Starting VITON processing for job {job_id}")
        
        # Step 1: Pose Estimation
        print("🕺 Detecting pose...")
        pose_results = await pose_estimator.detect_pose(person_image_path)
        if not pose_results["success"]:
            raise Exception("Pose detection failed")
        
        # Step 2: Human Parsing
        print("👤 Parsing human segments...")
        parsing_results = await human_parser.parse_human(person_image_path)
        if not parsing_results["success"]:
            raise Exception("Human parsing failed")
        
        # Step 3: Clothing Segmentation & Removal
        print("👕 Segmenting and removing existing clothing...")
        clothing_mask = await human_parser.get_clothing_mask(
            person_image_path, category
        )
        
        # Step 4: Garment Analysis
        print("👗 Analyzing target garment...")
        garment_features = await viton_pipeline.analyze_garment(
            garment_image_path, category
        )
        
        # Step 5: VITON-HD Processing
        print("🎨 Generating virtual try-on...")
        viton_result = await viton_pipeline.generate_tryon(
            person_image=person_image_path,
            garment_image=garment_image_path,
            pose_keypoints=pose_results["keypoints"],
            human_parse_map=parsing_results["parse_map"],
            clothing_mask=clothing_mask,
            category=category,
            preserve_background=preserve_background,
            high_quality=high_quality
        )
        
        if not viton_result["success"]:
            raise Exception(f"VITON generation failed: {viton_result['error']}")
        
        # Step 6: Post-processing
        print("✨ Post-processing result...")
        final_result = await viton_pipeline.post_process(
            viton_result["result_image"],
            enhance_quality=high_quality
        )
        
        # Save result
        result_path = f"results/{job_id}_viton_real.jpg"
        final_result.save(result_path, "JPEG", quality=95, optimize=True)
        
        processing_time = time.time() - start_time
        
        print(f"✅ VITON processing completed in {processing_time:.2f}s")
        
        return VITONResponse(
            job_id=job_id,
            status="completed",
            result_url=f"/results/{job_id}_viton_real.jpg",
            pose_keypoints=pose_results["keypoints"],
            segmentation_mask=f"/temp/{job_id}_segmentation.png",
            processing_time=round(processing_time, 2),
            message="Real VITON-HD processing completed successfully",
            model_info={
                "viton_model": "VITON-HD-512",
                "pose_model": "MediaPipe",
                "parser_model": "ATR-ResNet",
                "gpu_used": viton_pipeline.gpu_available
            }
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"VITON processing failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        return VITONResponse(
            job_id=job_id,
            status="failed",
            message=error_msg,
            processing_time=round(processing_time, 2)
        )

@app.post("/process-viton-real", response_model=VITONResponse)
async def process_viton_endpoint(
    background_tasks: BackgroundTasks,
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    job_id: str = None,
    category: str = "upper_body",
    preserve_background: bool = True,
    high_quality: bool = True
):
    """Process real VITON-HD virtual try-on"""
    
    if not job_id:
        job_id = str(uuid.uuid4())
    
    try:
        # Save uploaded files
        person_temp_path = f"temp/{job_id}_person_{person_image.filename}"
        garment_temp_path = f"temp/{job_id}_garment_{garment_image.filename}"
        
        with open(person_temp_path, "wb") as f:
            content = await person_image.read()
            f.write(content)
        
        with open(garment_temp_path, "wb") as f:
            content = await garment_image.read()
            f.write(content)
        
        # Add to processing queue
        processing_jobs[job_id] = {
            "status": "processing",
            "started_at": time.time(),
            "category": category
        }
        
        # Process VITON
        result = await process_viton_real(
            person_temp_path,
            garment_temp_path,
            job_id,
            category,
            preserve_background,
            high_quality
        )
        
        # Update job status
        processing_jobs[job_id] = {
            "status": result.status,
            "completed_at": time.time(),
            "result": result
        }
        
        # Cleanup temp files
        background_tasks.add_task(cleanup_temp_files, [person_temp_path, garment_temp_path])
        
        return result
        
    except Exception as e:
        return VITONResponse(
            job_id=job_id,
            status="failed",
            message=f"Request processing failed: {str(e)}"
        )

@app.get("/jobs/{job_id}", response_model=VITONResponse)
async def get_job_status(job_id: str):
    """Get processing job status"""
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = processing_jobs[job_id]
    
    if job_data["status"] == "completed" and "result" in job_data:
        return job_data["result"]
    else:
        return VITONResponse(
            job_id=job_id,
            status=job_data["status"],
            message=f"Job {job_data['status']}..."
        )

def cleanup_temp_files(file_paths: List[str]):
    """Background task to cleanup temporary files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Failed to cleanup {file_path}: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8002,
        reload=True,
        log_level="info"
    )