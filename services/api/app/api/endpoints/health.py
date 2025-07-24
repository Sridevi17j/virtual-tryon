from fastapi import APIRouter, HTTPException
from datetime import datetime
from loguru import logger

from ...services.ml_client import ml_client
from ...services.storage import storage_service
from ...services.job_manager import job_manager
from ...models.schemas import HealthResponse

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check for all services"""
    
    try:
        services = {}
        
        # Check ML service
        try:
            ml_status = await ml_client.health_check()
            services["ml_service"] = ml_status
        except Exception as e:
            services["ml_service"] = {"status": "unhealthy", "error": str(e)}
        
        # Check storage service
        try:
            storage_status = await storage_service.health_check()
            services["storage"] = storage_status
        except Exception as e:
            services["storage"] = {"status": "unhealthy", "error": str(e)}
        
        # Check job manager (Redis)
        try:
            if job_manager.redis_client:
                await job_manager.redis_client.ping()
                services["job_manager"] = {"status": "healthy", "type": "redis"}
            else:
                services["job_manager"] = {"status": "degraded", "type": "in-memory"}
        except Exception as e:
            services["job_manager"] = {"status": "unhealthy", "error": str(e)}
        
        # Determine overall status
        unhealthy_services = [name for name, status in services.items() 
                            if status.get("status") != "healthy"]
        
        if not unhealthy_services:
            overall_status = "healthy"
        elif len(unhealthy_services) == len(services):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        return HealthResponse(
            status=overall_status,
            services=services,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/ml")
async def ml_service_health():
    """Check ML service health specifically"""
    
    try:
        status = await ml_client.health_check()
        return status
    except Exception as e:
        logger.error(f"ML service health check failed: {e}")
        raise HTTPException(status_code=503, detail="ML service unavailable")

@router.get("/storage")
async def storage_health():
    """Check storage service health specifically"""
    
    try:
        status = await storage_service.health_check()
        return status
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        raise HTTPException(status_code=503, detail="Storage service unavailable")

@router.get("/jobs")
async def job_manager_health():
    """Check job manager health specifically"""
    
    try:
        if job_manager.redis_client:
            await job_manager.redis_client.ping()
            return {"status": "healthy", "type": "redis"}
        else:
            return {"status": "degraded", "type": "in-memory", "message": "Redis not available"}
    except Exception as e:
        logger.error(f"Job manager health check failed: {e}")
        raise HTTPException(status_code=503, detail="Job manager unavailable")

@router.get("/readiness")
async def readiness_check():
    """Readiness probe for Kubernetes/container orchestration"""
    
    try:
        # Check critical services only
        ml_status = await ml_client.health_check()
        storage_status = await storage_service.health_check()
        
        if (ml_status.get("status") == "healthy" and 
            storage_status.get("status") == "healthy"):
            return {"status": "ready"}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/liveness")
async def liveness_check():
    """Liveness probe for Kubernetes/container orchestration"""
    
    # Simple check that the application is running
    return {"status": "alive", "timestamp": datetime.now()}