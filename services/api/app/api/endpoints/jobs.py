from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from loguru import logger

from ...services.job_manager import job_manager
from ...models.schemas import JobInfo, JobStatus

router = APIRouter()

@router.get("/{job_id}", response_model=JobInfo)
async def get_job_status(job_id: str):
    """Get job status by ID"""
    
    try:
        job = await job_manager.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job status")

@router.get("/", response_model=List[JobInfo])
async def list_jobs(
    status: Optional[JobStatus] = Query(None, description="Filter by job status"),
    limit: int = Query(100, description="Maximum number of jobs to return", le=1000)
):
    """List jobs with optional filtering"""
    
    try:
        jobs = await job_manager.list_jobs(limit=limit)
        
        # Filter by status if provided
        if status:
            jobs = [job for job in jobs if job.status == status]
        
        return jobs
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")

@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete job and its data"""
    
    try:
        success = await job_manager.delete_job(job_id)
        
        if success:
            return {"message": "Job deleted successfully", "job_id": job_id}
        else:
            raise HTTPException(status_code=404, detail="Job not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete job")

@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    
    try:
        job = await job_manager.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            raise HTTPException(status_code=400, detail="Job is already finished")
        
        # Update job status to failed (cancelled)
        updated_job = await job_manager.update_job_status(
            job_id, 
            JobStatus.FAILED, 
            error="Job cancelled by user"
        )
        
        return {
            "message": "Job cancelled successfully",
            "job_id": job_id,
            "status": "cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel job")

@router.get("/stats/summary")
async def get_job_stats():
    """Get job statistics summary"""
    
    try:
        jobs = await job_manager.list_jobs(limit=1000)
        
        stats = {
            "total": len(jobs),
            "pending": sum(1 for job in jobs if job.status == JobStatus.PENDING),
            "processing": sum(1 for job in jobs if job.status == JobStatus.PROCESSING),
            "completed": sum(1 for job in jobs if job.status == JobStatus.COMPLETED),
            "failed": sum(1 for job in jobs if job.status == JobStatus.FAILED)
        }
        
        # Calculate success rate
        total_finished = stats["completed"] + stats["failed"]
        if total_finished > 0:
            stats["success_rate"] = stats["completed"] / total_finished
        else:
            stats["success_rate"] = 0.0
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get job stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job statistics")

@router.post("/cleanup")
async def cleanup_expired_jobs():
    """Manually trigger cleanup of expired jobs"""
    
    try:
        await job_manager.cleanup_expired_jobs()
        
        return {"message": "Expired jobs cleanup completed"}
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup expired jobs")