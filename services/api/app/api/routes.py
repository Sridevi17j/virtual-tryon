from fastapi import APIRouter
from .endpoints import upload, tryon, jobs, health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
api_router.include_router(tryon.router, prefix="/tryon", tags=["Virtual Try-On"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])