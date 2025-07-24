from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import uuid
from datetime import datetime
from loguru import logger

from ...core.config import settings
from ...services.storage import storage_service
from ...models.schemas import FileUploadResponse

router = APIRouter()

@router.post("/", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a single file"""
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} not allowed. Supported types: {settings.ALLOWED_IMAGE_TYPES}"
        )
    
    # Validate file size
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size {file.size} exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        file_url = await storage_service.save_upload(file, file_id)
        
        logger.info(f"File uploaded successfully: {file.filename} -> {file_id}")
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_url=file_url,
            file_size=file.size,
            content_type=file.content_type,
            uploaded_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/multiple", response_model=List[FileUploadResponse])
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload multiple files"""
    
    if len(files) > 10:  # Limit to 10 files
        raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files allowed.")
    
    results = []
    
    for file in files:
        try:
            # Validate file type
            if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
                logger.warning(f"Skipping file {file.filename}: invalid type {file.content_type}")
                continue
            
            # Validate file size
            if file.size > settings.MAX_FILE_SIZE:
                logger.warning(f"Skipping file {file.filename}: too large ({file.size} bytes)")
                continue
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Save file
            file_url = await storage_service.save_upload(file, file_id)
            
            results.append(FileUploadResponse(
                file_id=file_id,
                filename=file.filename,
                file_url=file_url,
                file_size=file.size,
                content_type=file.content_type,
                uploaded_at=datetime.now()
            ))
            
            logger.info(f"File uploaded successfully: {file.filename} -> {file_id}")
            
        except Exception as e:
            logger.error(f"Failed to upload file {file.filename}: {e}")
            # Continue with other files
            continue
    
    if not results:
        raise HTTPException(status_code=400, detail="No files were successfully uploaded")
    
    return results

@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file"""
    
    try:
        success = await storage_service.delete_file(file_id)
        
        if success:
            logger.info(f"File deleted successfully: {file_id}")
            return {"message": "File deleted successfully", "file_id": file_id}
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except Exception as e:
        logger.error(f"File deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.get("/{file_id}/exists")
async def check_file_exists(file_id: str):
    """Check if file exists"""
    
    try:
        exists = await storage_service.file_exists(file_id)
        
        return {
            "file_id": file_id,
            "exists": exists
        }
        
    except Exception as e:
        logger.error(f"File existence check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Check failed: {str(e)}")

@router.get("/limits")
async def get_upload_limits():
    """Get upload limits and constraints"""
    
    return {
        "max_file_size": settings.MAX_FILE_SIZE,
        "max_files": 10,
        "allowed_types": settings.ALLOWED_IMAGE_TYPES,
        "max_file_size_mb": settings.MAX_FILE_SIZE / (1024 * 1024)
    }