import redis.asyncio as redis
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from loguru import logger

from ..core.config import settings
from ..models.schemas import JobStatus, JobInfo

class JobManager:
    """Manage job status and tracking using Redis"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.job_prefix = "job:"
        self.job_expiry = timedelta(hours=24)  # Jobs expire after 24 hours
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Job manager (Redis) initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            # Continue without Redis for development
            self.redis_client = None
    
    async def cleanup(self):
        """Cleanup Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Job manager cleanup completed")
    
    async def create_job(
        self,
        job_id: str,
        person_image_url: Optional[str] = None,
        garment_image_url: Optional[str] = None
    ) -> JobInfo:
        """Create a new job"""
        now = datetime.now()
        
        job_data = {
            "job_id": job_id,
            "status": JobStatus.PENDING,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "person_image_url": person_image_url,
            "garment_image_url": garment_image_url
        }
        
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"{self.job_prefix}{job_id}",
                    self.job_expiry,
                    json.dumps(job_data)
                )
                logger.debug(f"Created job in Redis: {job_id}")
            except Exception as e:
                logger.error(f"Failed to create job in Redis: {e}")
        
        return JobInfo(**job_data)
    
    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result_url: Optional[str] = None,
        error: Optional[str] = None
    ) -> Optional[JobInfo]:
        """Update job status"""
        try:
            if self.redis_client:
                # Get existing job data
                job_key = f"{self.job_prefix}{job_id}"
                job_data_str = await self.redis_client.get(job_key)
                
                if job_data_str:
                    job_data = json.loads(job_data_str)
                else:
                    # Create new job data if doesn't exist
                    job_data = {
                        "job_id": job_id,
                        "created_at": datetime.now().isoformat()
                    }
                
                # Update fields
                job_data["status"] = status
                job_data["updated_at"] = datetime.now().isoformat()
                
                if result_url:
                    job_data["result_url"] = result_url
                
                if error:
                    job_data["error"] = error
                
                if status == JobStatus.COMPLETED:
                    job_data["completed_at"] = datetime.now().isoformat()
                
                # Save updated data
                await self.redis_client.setex(
                    job_key,
                    self.job_expiry,
                    json.dumps(job_data)
                )
                
                logger.debug(f"Updated job status: {job_id} -> {status}")
                return JobInfo(**job_data)
            else:
                # Without Redis, just log the status update
                logger.info(f"Job {job_id} status updated to {status}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            return None
    
    async def get_job_status(self, job_id: str) -> Optional[JobInfo]:
        """Get job status"""
        try:
            if self.redis_client:
                job_key = f"{self.job_prefix}{job_id}"
                job_data_str = await self.redis_client.get(job_key)
                
                if job_data_str:
                    job_data = json.loads(job_data_str)
                    return JobInfo(**job_data)
                else:
                    logger.warning(f"Job not found: {job_id}")
                    return None
            else:
                # Without Redis, return mock data
                return JobInfo(
                    job_id=job_id,
                    status=JobStatus.PENDING,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return None
    
    async def list_jobs(self, limit: int = 100) -> List[JobInfo]:
        """List recent jobs"""
        jobs = []
        
        try:
            if self.redis_client:
                # Get all job keys
                job_keys = await self.redis_client.keys(f"{self.job_prefix}*")
                
                # Get job data for each key
                if job_keys:
                    # Limit the number of keys to process
                    job_keys = job_keys[:limit]
                    
                    for job_key in job_keys:
                        job_data_str = await self.redis_client.get(job_key)
                        if job_data_str:
                            job_data = json.loads(job_data_str)
                            jobs.append(JobInfo(**job_data))
                
                # Sort by created_at (most recent first)
                jobs.sort(key=lambda x: x.created_at, reverse=True)
                
        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
        
        return jobs
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete job from storage"""
        try:
            if self.redis_client:
                job_key = f"{self.job_prefix}{job_id}"
                result = await self.redis_client.delete(job_key)
                
                if result:
                    logger.debug(f"Deleted job: {job_id}")
                    return True
                else:
                    logger.warning(f"Job not found for deletion: {job_id}")
                    return False
            else:
                return True  # Always succeed without Redis
                
        except Exception as e:
            logger.error(f"Failed to delete job: {e}")
            return False
    
    async def cleanup_expired_jobs(self):
        """Clean up expired jobs (called periodically)"""
        try:
            if self.redis_client:
                cutoff_time = datetime.now() - self.job_expiry
                
                job_keys = await self.redis_client.keys(f"{self.job_prefix}*")
                expired_count = 0
                
                for job_key in job_keys:
                    job_data_str = await self.redis_client.get(job_key)
                    if job_data_str:
                        job_data = json.loads(job_data_str)
                        created_at = datetime.fromisoformat(job_data["created_at"])
                        
                        if created_at < cutoff_time:
                            await self.redis_client.delete(job_key)
                            expired_count += 1
                
                if expired_count > 0:
                    logger.info(f"Cleaned up {expired_count} expired jobs")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup expired jobs: {e}")

# Global job manager instance
job_manager = JobManager()