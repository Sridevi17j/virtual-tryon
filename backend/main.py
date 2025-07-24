from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import uuid
import os
from pathlib import Path
from typing import Optional
import json
import time
from PIL import Image, ImageDraw, ImageFont
import glob
import httpx
import asyncio

# Create directories
Path("uploads").mkdir(exist_ok=True)
Path("results").mkdir(exist_ok=True)

app = FastAPI(
    title="Virtual Try-On API",
    description="Simple API for virtual fashion try-on demo",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/results", StaticFiles(directory="results"), name="results")

# Configuration
ENHANCED_ML_SERVICE_URL = "http://127.0.0.1:8001"  # Enhanced ML service with API fallbacks

# In-memory storage for demo
jobs = {}

def create_demo_result(job_id: str):
    """Create a simple demo result by combining person and garment images"""
    try:
        # Find the uploaded images for this job
        person_files = glob.glob(f"uploads/{job_id}_person_*")
        garment_files = glob.glob(f"uploads/{job_id}_garment_*")
        
        if not person_files or not garment_files:
            raise Exception("Could not find uploaded images")
        
        # Open the images
        person_img = Image.open(person_files[0])
        garment_img = Image.open(garment_files[0])
        
        # Resize images to a standard size
        target_size = (400, 600)
        person_img = person_img.resize(target_size, Image.Resampling.LANCZOS)
        garment_img = garment_img.resize((200, 300), Image.Resampling.LANCZOS)
        
        # Create a new image for the result
        result_img = person_img.copy()
        
        # Create a simple overlay effect (paste garment in top-right corner with transparency)
        # Convert to RGBA if needed
        if garment_img.mode != 'RGBA':
            garment_img = garment_img.convert('RGBA')
        
        # Make the garment semi-transparent
        garment_overlay = Image.new('RGBA', garment_img.size, (255, 255, 255, 0))
        garment_overlay = Image.blend(garment_overlay, garment_img, 0.7)
        
        # Paste the garment overlay on the person image
        result_img.paste(garment_overlay, (180, 50), garment_overlay)
        
        # Add some text to indicate this is a demo
        draw = ImageDraw.Draw(result_img)
        try:
            # Try to use a default font, fall back to basic if not available
            font = ImageFont.load_default()
        except:
            font = None
        
        # Add demo watermark
        draw.text((10, 10), "DEMO RESULT", fill=(255, 255, 255), font=font)
        draw.text((10, 30), "Virtual Try-On", fill=(255, 255, 255), font=font)
        
        # Save the result
        result_path = f"results/{job_id}_result.jpg"
        result_img.convert('RGB').save(result_path, 'JPEG', quality=85)
        
        return result_path
        
    except Exception as e:
        print(f"Error creating demo result: {e}")
        raise e

async def process_with_enhanced_ml_service(job_id: str):
    """Process virtual try-on using the enhanced ML service with API fallbacks"""
    try:
        # Find the uploaded images for this job
        person_files = glob.glob(f"uploads/{job_id}_person_*")
        garment_files = glob.glob(f"uploads/{job_id}_garment_*")
        
        if not person_files or not garment_files:
            raise Exception("Could not find uploaded images")
        
        # Prepare files for enhanced ML service
        person_file_path = person_files[0]
        garment_file_path = garment_files[0]
        
        async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout for API calls
            # Check if enhanced ML service is available
            try:
                health_response = await client.get(f"{ENHANCED_ML_SERVICE_URL}/health")
                if health_response.status_code != 200:
                    raise Exception("Enhanced ML service is not healthy")
            except httpx.RequestError:
                raise Exception("Enhanced ML service is not available")
            
            # Prepare files for upload to enhanced ML service
            with open(person_file_path, "rb") as person_file, open(garment_file_path, "rb") as garment_file:
                files = {
                    "person_image": (os.path.basename(person_file_path), person_file, "image/jpeg"),
                    "garment_image": (os.path.basename(garment_file_path), garment_file, "image/jpeg")
                }
                
                data = {"job_id": job_id}
                
                # Call enhanced ML service
                response = await client.post(
                    f"{ENHANCED_ML_SERVICE_URL}/process-tryon",
                    files=files,
                    data=data
                )
            
            if response.status_code != 200:
                raise Exception(f"Enhanced ML service error: {response.status_code}")
            
            result = response.json()
            
            if result["status"] == "completed":
                # Download the result image from enhanced ML service
                result_response = await client.get(f"{ENHANCED_ML_SERVICE_URL}{result['result_url']}")
                if result_response.status_code == 200:
                    # Save the result locally
                    local_result_path = f"results/{job_id}_result.jpg"
                    with open(local_result_path, "wb") as f:
                        f.write(result_response.content)
                    return local_result_path, result.get("message", "Processing completed")
                else:
                    raise Exception("Failed to download result from enhanced ML service")
            else:
                raise Exception(result.get("message", "Enhanced ML processing failed"))
                
    except Exception as e:
        print(f"Error processing with enhanced ML service: {e}")
        raise e

class JobStatus(BaseModel):
    job_id: str
    status: str
    message: Optional[str] = None
    result_url: Optional[str] = None
    created_at: float
    completed_at: Optional[float] = None

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
    return {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "storage": "healthy"
        }
    }

@app.post("/api/v1/tryon")
async def create_tryon_job(
    person_image: UploadFile = File(...),
    garment_image: UploadFile = File(...)
):
    """Create a virtual try-on job"""
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded files
        person_filename = f"{job_id}_person_{person_image.filename}"
        garment_filename = f"{job_id}_garment_{garment_image.filename}"
        
        person_path = f"uploads/{person_filename}"
        garment_path = f"uploads/{garment_filename}"
        
        # Save person image
        with open(person_path, "wb") as f:
            content = await person_image.read()
            f.write(content)
        
        # Save garment image
        with open(garment_path, "wb") as f:
            content = await garment_image.read()
            f.write(content)
        
        # Create job record
        job = JobStatus(
            job_id=job_id,
            status="processing",
            message="Virtual try-on processing started",
            created_at=time.time()
        )
        
        jobs[job_id] = job
        
        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Virtual try-on job created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # Process job after 2 seconds delay (to allow for uploads to complete)
    if job.status == "processing" and time.time() - job.created_at > 2:
        try:
            print(f"Processing job {job_id} with Enhanced ML service...")
            # Try Enhanced ML service first (with API fallbacks)
            result_path, service_message = await process_with_enhanced_ml_service(job_id)
            job.status = "completed"
            job.message = service_message
            job.completed_at = time.time()
            job.result_url = f"/results/{job_id}_result.jpg"
            print(f"Enhanced ML service processing completed for job {job_id}")
            
        except Exception as ml_error:
            print(f"Enhanced ML service failed for job {job_id}: {ml_error}")
            print("Falling back to basic demo processing...")
            
            # Fallback to basic demo processing
            try:
                create_demo_result(job_id)
                job.status = "completed"
                job.message = "Virtual try-on completed with basic demo processing (Enhanced ML service unavailable)"
                job.completed_at = time.time()
                job.result_url = f"/results/{job_id}_result.jpg"
                print(f"Basic demo processing completed for job {job_id}")
                
            except Exception as demo_error:
                job.status = "failed"
                job.message = f"Both Enhanced ML and demo processing failed: {str(demo_error)}"
                print(f"All processing failed for job {job_id}: {demo_error}")
    
    return job.dict()

@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs"""
    return list(jobs.values())

@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Clean up files
    try:
        person_files = Path("uploads").glob(f"{job_id}_person_*")
        garment_files = Path("uploads").glob(f"{job_id}_garment_*")
        result_files = Path("results").glob(f"{job_id}_result.*")
        
        for file_path in list(person_files) + list(garment_files) + list(result_files):
            if file_path.exists():
                file_path.unlink()
    except Exception as e:
        print(f"Warning: Failed to clean up files for job {job_id}: {e}")
    
    del jobs[job_id]
    return {"message": "Job deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )