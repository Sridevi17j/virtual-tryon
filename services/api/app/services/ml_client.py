import httpx
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
import asyncio

from ..core.config import settings

class MLClient:
    """Client for communicating with the ML service"""
    
    def __init__(self):
        self.base_url = settings.ML_SERVICE_URL
        self.timeout = settings.ML_SERVICE_TIMEOUT
        self.client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )
        logger.info(f"ML client initialized with base URL: {self.base_url}")
    
    async def cleanup(self):
        """Cleanup HTTP client"""
        if self.client:
            await self.client.aclose()
            logger.info("ML client closed")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check ML service health"""
        try:
            if not self.client:
                await self.initialize()
            
            response = await self.client.get("/health")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"ML service health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def virtual_try_on(self, person_image_path: str, garment_image_path: str) -> bytes:
        """
        Perform virtual try-on using ML service
        
        Args:
            person_image_path: Path to person image
            garment_image_path: Path to garment image
            
        Returns:
            Result image as bytes
        """
        try:
            if not self.client:
                await self.initialize()
            
            # Prepare multipart form data
            files = {
                "person_image": (
                    Path(person_image_path).name,
                    open(person_image_path, "rb"),
                    "image/jpeg"
                ),
                "garment_image": (
                    Path(garment_image_path).name,
                    open(garment_image_path, "rb"),
                    "image/jpeg"
                )
            }
            
            logger.info(f"Sending try-on request to ML service...")
            
            response = await self.client.post("/try-on", files=files)
            
            # Close file handles
            for _, file_info in files.items():
                if hasattr(file_info[1], 'close'):
                    file_info[1].close()
            
            response.raise_for_status()
            
            logger.info("Try-on request completed successfully")
            return response.content
            
        except httpx.HTTPStatusError as e:
            logger.error(f"ML service returned error {e.response.status_code}: {e.response.text}")
            raise Exception(f"ML service error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Virtual try-on failed: {e}")
            raise Exception(f"Virtual try-on failed: {str(e)}")
    
    async def preprocess_image(self, image_path: str, image_type: str) -> bytes:
        """
        Preprocess image using ML service
        
        Args:
            image_path: Path to image
            image_type: Type of image ('person' or 'garment')
            
        Returns:
            Preprocessed image as bytes
        """
        try:
            if not self.client:
                await self.initialize()
            
            files = {
                "image": (
                    Path(image_path).name,
                    open(image_path, "rb"),
                    "image/jpeg"
                )
            }
            
            data = {"image_type": image_type}
            
            logger.info(f"Sending preprocess request for {image_type} image...")
            
            response = await self.client.post("/preprocess", files=files, data=data)
            
            # Close file handle
            files["image"][1].close()
            
            response.raise_for_status()
            
            logger.info("Preprocessing completed successfully")
            return response.content
            
        except httpx.HTTPStatusError as e:
            logger.error(f"ML service returned error {e.response.status_code}: {e.response.text}")
            raise Exception(f"ML service error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise Exception(f"Preprocessing failed: {str(e)}")
    
    async def estimate_pose(self, image_path: str) -> Dict[str, Any]:
        """
        Estimate pose from image using ML service
        
        Args:
            image_path: Path to person image
            
        Returns:
            Pose estimation data
        """
        try:
            if not self.client:
                await self.initialize()
            
            files = {
                "image": (
                    Path(image_path).name,
                    open(image_path, "rb"),
                    "image/jpeg"
                )
            }
            
            logger.info("Sending pose estimation request...")
            
            response = await self.client.post("/pose", files=files)
            
            # Close file handle
            files["image"][1].close()
            
            response.raise_for_status()
            
            logger.info("Pose estimation completed successfully")
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"ML service returned error {e.response.status_code}: {e.response.text}")
            raise Exception(f"ML service error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Pose estimation failed: {e}")
            raise Exception(f"Pose estimation failed: {str(e)}")

# Global ML client instance
ml_client = MLClient()