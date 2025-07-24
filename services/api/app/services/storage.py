import aiofiles
from minio import Minio
from minio.error import S3Error
from pathlib import Path
from typing import Optional
import uuid
import asyncio
from datetime import datetime, timedelta
from loguru import logger
from fastapi import UploadFile
import tempfile
import os

from ..core.config import settings

class StorageService:
    """Storage service for handling file uploads and results"""
    
    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.client: Optional[Minio] = None
        self.bucket_name = settings.MINIO_BUCKET
        
        # Create local directories if using local storage
        if self.storage_type == "local":
            Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
            Path(settings.TEMP_DIR).mkdir(exist_ok=True)
    
    async def initialize(self):
        """Initialize storage service"""
        if self.storage_type == "minio":
            try:
                # Parse MinIO URL
                url_parts = settings.STORAGE_URL.replace("http://", "").replace("https://", "")
                endpoint = url_parts.split("/")[0]
                secure = settings.STORAGE_URL.startswith("https://")
                
                self.client = Minio(
                    endpoint,
                    access_key=settings.MINIO_ACCESS_KEY,
                    secret_key=settings.MINIO_SECRET_KEY,
                    secure=secure
                )
                
                # Create bucket if it doesn't exist
                if not self.client.bucket_exists(self.bucket_name):
                    self.client.make_bucket(self.bucket_name)
                    logger.info(f"Created bucket: {self.bucket_name}")
                
                logger.info(f"MinIO storage initialized: {endpoint}")
                
            except Exception as e:
                logger.error(f"Failed to initialize MinIO storage: {e}")
                raise
        else:
            logger.info(f"Local storage initialized: {settings.UPLOAD_DIR}")
    
    async def cleanup(self):
        """Cleanup storage service"""
        # No cleanup needed for MinIO client
        logger.info("Storage service cleanup completed")
    
    async def health_check(self) -> dict:
        """Check storage service health"""
        try:
            if self.storage_type == "minio" and self.client:
                # Try to list objects in bucket
                list(self.client.list_objects(self.bucket_name, max_keys=1))
                return {"status": "healthy", "type": "minio"}
            else:
                # Check if local directories exist and are writable
                upload_dir = Path(settings.UPLOAD_DIR)
                if upload_dir.exists() and os.access(upload_dir, os.W_OK):
                    return {"status": "healthy", "type": "local"}
                else:
                    return {"status": "unhealthy", "type": "local", "error": "Directory not writable"}
                    
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def save_upload(self, file: UploadFile, filename: Optional[str] = None) -> str:
        """
        Save uploaded file
        
        Args:
            file: FastAPI UploadFile object
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        try:
            # Generate filename if not provided
            if not filename:
                file_extension = Path(file.filename).suffix if file.filename else ".jpg"
                filename = f"{uuid.uuid4()}{file_extension}"
            elif not Path(filename).suffix:
                file_extension = Path(file.filename).suffix if file.filename else ".jpg"
                filename = f"{filename}{file_extension}"
            
            if self.storage_type == "minio" and self.client:
                return await self._save_to_minio(file, filename)
            else:
                return await self._save_to_local(file, filename)
                
        except Exception as e:
            logger.error(f"Failed to save upload: {e}")
            raise
    
    async def save_result(self, data: bytes, filename: str) -> str:
        """
        Save processing result
        
        Args:
            data: File data as bytes
            filename: Filename for the result
            
        Returns:
            URL to saved file
        """
        try:
            if self.storage_type == "minio" and self.client:
                return await self._save_bytes_to_minio(data, filename)
            else:
                return await self._save_bytes_to_local(data, filename)
                
        except Exception as e:
            logger.error(f"Failed to save result: {e}")
            raise
    
    async def _save_to_minio(self, file: UploadFile, filename: str) -> str:
        """Save file to MinIO"""
        try:
            # Reset file pointer
            await file.seek(0)
            
            # Upload to MinIO
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=filename,
                data=file.file,
                length=file.size,
                content_type=file.content_type
            )
            
            # Generate presigned URL for access
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=filename,
                expires=timedelta(hours=24)
            )
            
            logger.debug(f"Saved file to MinIO: {filename}")
            return url
            
        except S3Error as e:
            logger.error(f"MinIO error: {e}")
            raise Exception(f"Storage error: {e}")
    
    async def _save_to_local(self, file: UploadFile, filename: str) -> str:
        """Save file to local storage"""
        try:
            file_path = Path(settings.UPLOAD_DIR) / filename
            
            # Reset file pointer
            await file.seek(0)
            
            # Write file
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)
            
            logger.debug(f"Saved file locally: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Local storage error: {e}")
            raise
    
    async def _save_bytes_to_minio(self, data: bytes, filename: str) -> str:
        """Save bytes data to MinIO"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile() as tmp_file:
                tmp_file.write(data)
                tmp_file.flush()
                tmp_file.seek(0)
                
                # Upload to MinIO
                self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=filename,
                    data=tmp_file,
                    length=len(data),
                    content_type="image/jpeg"
                )
            
            # Generate presigned URL
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=filename,
                expires=timedelta(hours=24)
            )
            
            logger.debug(f"Saved result to MinIO: {filename}")
            return url
            
        except S3Error as e:
            logger.error(f"MinIO error: {e}")
            raise Exception(f"Storage error: {e}")
    
    async def _save_bytes_to_local(self, data: bytes, filename: str) -> str:
        """Save bytes data to local storage"""
        try:
            file_path = Path(settings.UPLOAD_DIR) / filename
            
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(data)
            
            logger.debug(f"Saved result locally: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Local storage error: {e}")
            raise
    
    async def delete_file(self, filename: str) -> bool:
        """Delete file from storage"""
        try:
            if self.storage_type == "minio" and self.client:
                self.client.remove_object(self.bucket_name, filename)
                logger.debug(f"Deleted from MinIO: {filename}")
            else:
                file_path = Path(settings.UPLOAD_DIR) / filename
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Deleted locally: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {filename}: {e}")
            return False
    
    async def file_exists(self, filename: str) -> bool:
        """Check if file exists in storage"""
        try:
            if self.storage_type == "minio" and self.client:
                try:
                    self.client.stat_object(self.bucket_name, filename)
                    return True
                except S3Error:
                    return False
            else:
                file_path = Path(settings.UPLOAD_DIR) / filename
                return file_path.exists()
                
        except Exception as e:
            logger.error(f"Failed to check file existence {filename}: {e}")
            return False

# Global storage service instance
storage_service = StorageService()