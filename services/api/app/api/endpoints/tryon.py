from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import asyncio
import uuid
from pathlib import Path
from loguru import logger

from ...core.config import settings
from ...services.ml_client import ml_client
from ...services.storage import storage_service
from ...services.job_manager import job_manager
from ...models.schemas import TryOnRequest, TryOnResponse, JobStatus

router = APIRouter()

@router.post("/", response_model=TryOnResponse)
async def virtual_try_on(
    background_tasks: BackgroundTasks,
    person_image: UploadFile = File(..., description="Person image"),
    garment_image: UploadFile = File(..., description="Garment image"),
    async_processing: bool = False
):
    """
    Perform virtual try-on
    """
    # Validate files
    if not person_image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Person file must be an image")
    
    if not garment_image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Garment file must be an image")
    
    # Check file sizes
    if person_image.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Person image too large")
    
    if garment_image.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Garment image too large")
    
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded files
        person_path = await storage_service.save_upload(person_image, f"person_{job_id}")
        garment_path = await storage_service.save_upload(garment_image, f"garment_{job_id}")
        
        if async_processing:
            # Start background processing
            background_tasks.add_task(
                process_tryon_async,
                job_id,
                person_path,
                garment_path
            )
            
            return TryOnResponse(
                job_id=job_id,
                status="processing",
                message="Virtual try-on started. Check job status for updates."
            )
        else:
            # Synchronous processing
            result_url = await process_tryon_sync(job_id, person_path, garment_path)
            
            return TryOnResponse(
                job_id=job_id,
                status="completed",
                result_url=result_url,
                message="Virtual try-on completed successfully."
            )
            
    except Exception as e:
        logger.error(f"Virtual try-on failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

async def process_tryon_sync(job_id: str, person_path: str, garment_path: str) -> str:
    """Process virtual try-on synchronously"""
    try:
        # Update job status
        await job_manager.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Call ML service
        result_data = await ml_client.virtual_try_on(person_path, garment_path)
        
        # Save result
        result_url = await storage_service.save_result(result_data, f"result_{job_id}.jpg")
        
        # Update job status
        await job_manager.update_job_status(job_id, JobStatus.COMPLETED, result_url=result_url)
        
        return result_url
        
    except Exception as e:
        await job_manager.update_job_status(job_id, JobStatus.FAILED, error=str(e))
        raise

async def process_tryon_async(job_id: str, person_path: str, garment_path: str):
    """Process virtual try-on asynchronously"""
    try:
        await process_tryon_sync(job_id, person_path, garment_path)
    except Exception as e:
        logger.error(f"Async processing failed for job {job_id}: {e}")

@router.get("/{job_id}/result")
async def get_tryon_result(job_id: str):
    """Get virtual try-on result by job ID"""
    try:
        job = await job_manager.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status == JobStatus.COMPLETED and job.result_url:
            # Return file or redirect to storage URL
            return FileResponse(job.result_url, media_type="image/jpeg")
        elif job.status == JobStatus.PROCESSING:
            return JSONResponse({"message": "Job still processing", "status": "processing"})
        elif job.status == JobStatus.FAILED:
            raise HTTPException(status_code=500, detail=f"Job failed: {job.error}")
        else:
            return JSONResponse({"message": "Job not completed", "status": job.status})
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get result for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get result")

@router.post("/preprocess")
async def preprocess_image(
    image: UploadFile = File(...),
    image_type: str = "person"  # person or garment
):
    """Preprocess image before try-on"""
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if image_type not in ["person", "garment"]:
        raise HTTPException(status_code=400, detail="image_type must be 'person' or 'garment'")
    
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = await storage_service.save_upload(image, f"{image_type}_{file_id}")
        
        # Call ML service for preprocessing
        processed_data = await ml_client.preprocess_image(file_path, image_type)
        
        # Save processed result
        result_url = await storage_service.save_result(
            processed_data, 
            f"processed_{image_type}_{file_id}.jpg"
        )
        
        return {
            "file_id": file_id,
            "processed_url": result_url,
            "original_filename": image.filename
        }
        
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {str(e)}")

@router.get("/examples")
async def get_examples():
    """Get example images for try-on"""
    # This could return URLs to example person and garment images
    return {
        "person_examples": [
            "/static/examples/person1.jpg",
            "/static/examples/person2.jpg",
            "/static/examples/person3.jpg"
        ],
        "garment_examples": [
            "/static/examples/shirt1.jpg",
            "/static/examples/dress1.jpg",
            "/static/examples/jacket1.jpg"
        ]
    }