from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import uuid
import os
import base64
import json
import time
import asyncio
from pathlib import Path
from typing import Optional
import httpx
import cv2
import numpy as np
from PIL import Image
import io

# Create directories
Path("temp").mkdir(exist_ok=True)
Path("results").mkdir(exist_ok=True)

app = FastAPI(
    title="Enhanced Virtual Try-On ML Service",
    description="Enhanced ML service using multiple API endpoints for virtual fashion try-on",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/results", StaticFiles(directory="results"), name="results")

class TryOnRequest(BaseModel):
    job_id: str
    person_image_url: Optional[str] = None
    garment_image_url: Optional[str] = None

class TryOnResponse(BaseModel):
    job_id: str
    status: str
    result_url: Optional[str] = None
    message: Optional[str] = None
    processing_time: Optional[float] = None

def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def base64_to_image(base64_string: str, output_path: str):
    """Convert base64 string to image file"""
    image_data = base64.b64decode(base64_string)
    with open(output_path, "wb") as image_file:
        image_file.write(image_data)

async def try_replicate_api(person_b64: str, garment_b64: str, job_id: str) -> Optional[str]:
    """Try using Replicate API for virtual try-on"""
    try:
        # Replicate API endpoint (example - you'd need actual API key)
        # This is a placeholder for demonstration
        print(f"Attempting Replicate API for job {job_id}...")
        
        # Simulate API call delay
        await asyncio.sleep(2)
        
        # For demo, return None to fall back to next method
        return None
        
    except Exception as e:
        print(f"Replicate API failed: {e}")
        return None

async def try_huggingface_api(person_b64: str, garment_b64: str, job_id: str) -> Optional[str]:
    """Try using Hugging Face Inference API"""
    try:
        print(f"Attempting Hugging Face API for job {job_id}...")
        
        # Example HF Inference API call (you'd need actual API key)
        headers = {
            "Authorization": "Bearer YOUR_HF_TOKEN",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": {
                "person_image": person_b64,
                "garment_image": garment_b64
            }
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # This is a placeholder endpoint
            response = await client.post(
                "https://api-inference.huggingface.co/models/virtual-tryon",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if "image" in result:
                    return result["image"]
        
        return None
        
    except Exception as e:
        print(f"Hugging Face API failed: {e}")
        return None

async def create_enhanced_demo_result(person_img_path: str, garment_img_path: str, job_id: str) -> str:
    """Create an enhanced demo result with better processing"""
    try:
        # Load images
        person_img = cv2.imread(person_img_path)
        garment_img = cv2.imread(garment_img_path)
        
        if person_img is None or garment_img is None:
            raise Exception("Could not load images")
        
        # Convert BGR to RGB
        person_img = cv2.cvtColor(person_img, cv2.COLOR_BGR2RGB)
        garment_img = cv2.cvtColor(garment_img, cv2.COLOR_BGR2RGB)
        
        # Resize to standard dimensions
        target_height, target_width = 1024, 768
        person_img = cv2.resize(person_img, (target_width, target_height))
        
        # Smart garment sizing based on aspect ratio
        garment_h, garment_w = garment_img.shape[:2]
        garment_aspect = garment_w / garment_h
        
        if garment_aspect > 1.2:  # Wide garment (shirts, tops)
            new_width = min(400, int(target_width * 0.6))
            new_height = int(new_width / garment_aspect)
        else:  # Tall garment (dresses, pants)
            new_height = min(500, int(target_height * 0.7))
            new_width = int(new_height * garment_aspect)
        
        garment_img = cv2.resize(garment_img, (new_width, new_height))
        
        # Create result image
        result_img = person_img.copy()
        
        # Enhanced positioning - try to detect person's torso area
        # Simple approach: position garment in upper-middle area
        x_offset = (target_width - new_width) // 2
        y_offset = int(target_height * 0.2)  # Start at 20% from top
        
        # Ensure garment fits within image bounds
        if y_offset + new_height > target_height:
            y_offset = target_height - new_height - 10
        
        # Create a more sophisticated blend
        # Extract region of interest from person image
        roi = result_img[y_offset:y_offset+new_height, x_offset:x_offset+new_width]
        
        # Create masks for better blending
        mask = np.ones((new_height, new_width, 3), dtype=np.float32)
        
        # Create soft edges
        edge_size = 20
        mask[:edge_size, :] *= np.linspace(0, 1, edge_size).reshape(-1, 1, 1)  # Top edge
        mask[-edge_size:, :] *= np.linspace(1, 0, edge_size).reshape(-1, 1, 1)  # Bottom edge
        mask[:, :edge_size] *= np.linspace(0, 1, edge_size).reshape(1, -1, 1)  # Left edge
        mask[:, -edge_size:] *= np.linspace(1, 0, edge_size).reshape(1, -1, 1)  # Right edge
        
        # Apply color matching (simple approach)
        # Match garment colors to person's lighting
        person_mean = np.mean(roi, axis=(0, 1))
        garment_mean = np.mean(garment_img, axis=(0, 1))
        
        # Adjust garment colors
        color_ratio = person_mean / (garment_mean + 1e-6)
        color_ratio = np.clip(color_ratio, 0.7, 1.3)  # Limit adjustment
        adjusted_garment = (garment_img * color_ratio).astype(np.uint8)
        
        # Blend images
        blended_roi = (mask * adjusted_garment + (1 - mask) * roi).astype(np.uint8)
        
        # Place blended region back
        result_img[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = blended_roi
        
        # Add some post-processing
        # Slight sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        result_img = cv2.filter2D(result_img, -1, kernel * 0.1 + np.eye(3) * 0.9)
        
        # Convert back to BGR for saving
        result_img = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
        
        # Add enhanced watermark
        cv2.putText(result_img, "ENHANCED AI TRY-ON", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(result_img, "Demo Mode v2.0", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Save result
        result_path = f"results/{job_id}_enhanced_result.jpg"
        cv2.imwrite(result_path, result_img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        
        return result_path
        
    except Exception as e:
        print(f"Enhanced demo processing failed: {e}")
        raise e

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Enhanced Virtual Try-On ML Service",
        "version": "2.0.0",
        "status": "running",
        "description": "Multi-API virtual try-on with enhanced demo fallback",
        "apis": ["replicate", "huggingface", "enhanced_demo"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "enhanced-ml-processing",
        "capabilities": [
            "multi-api-tryon", 
            "enhanced-demo-processing", 
            "color-matching",
            "smart-positioning"
        ]
    }

@app.post("/process-tryon", response_model=TryOnResponse)
async def process_tryon(
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...),
    job_id: str = Form(default=None)
):
    """
    Process virtual try-on with multiple API fallbacks
    """
    start_time = time.time()
    
    if not job_id:
        job_id = str(uuid.uuid4())
    
    try:
        # Save uploaded files temporarily
        person_temp_path = f"temp/{job_id}_person_{person_image.filename}"
        garment_temp_path = f"temp/{job_id}_garment_{garment_image.filename}"
        
        # Save person image
        with open(person_temp_path, "wb") as f:
            content = await person_image.read()
            f.write(content)
        
        # Save garment image
        with open(garment_temp_path, "wb") as f:
            content = await garment_image.read()
            f.write(content)
        
        # Convert images to base64 for API calls
        person_b64 = image_to_base64(person_temp_path)
        garment_b64 = image_to_base64(garment_temp_path)
        
        result_image_b64 = None
        api_used = "none"
        
        # Try multiple APIs in order of preference
        print(f"Starting multi-API processing for job {job_id}")
        
        # 1. Try Replicate API
        result_image_b64 = await try_replicate_api(person_b64, garment_b64, job_id)
        if result_image_b64:
            api_used = "replicate"
        
        # 2. Try Hugging Face API
        if not result_image_b64:
            result_image_b64 = await try_huggingface_api(person_b64, garment_b64, job_id)
            if result_image_b64:
                api_used = "huggingface"
        
        # 3. Fall back to enhanced demo processing
        if not result_image_b64:
            print(f"APIs unavailable, using enhanced demo processing for job {job_id}")
            result_path = await create_enhanced_demo_result(person_temp_path, garment_temp_path, job_id)
            api_used = "enhanced_demo"
        else:
            # Save API result
            result_path = f"results/{job_id}_api_result.jpg"
            base64_to_image(result_image_b64, result_path)
        
        # Clean up temp files
        try:
            os.unlink(person_temp_path)
            os.unlink(garment_temp_path)
        except:
            pass
        
        processing_time = time.time() - start_time
        
        return TryOnResponse(
            job_id=job_id,
            status="completed",
            result_url=f"/results/{os.path.basename(result_path)}",
            message=f"Virtual try-on completed using {api_used} (took {processing_time:.1f}s)",
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        # Clean up temp files on error
        try:
            if os.path.exists(person_temp_path):
                os.unlink(person_temp_path)
            if os.path.exists(garment_temp_path):
                os.unlink(garment_temp_path)
        except:
            pass
        
        processing_time = time.time() - start_time
        
        return TryOnResponse(
            job_id=job_id,
            status="failed",
            message=f"Enhanced ML processing failed: {str(e)}",
            processing_time=round(processing_time, 2)
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )