import os
from typing import List
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Virtual Try-On API"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="API_HOST")
    PORT: int = Field(default=8000, env="API_PORT")
    
    # Security settings
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # ML Service settings
    ML_SERVICE_URL: str = Field(default="http://localhost:8001", env="ML_SERVICE_URL")
    ML_SERVICE_TIMEOUT: int = 300  # 5 minutes
    
    # Storage settings
    STORAGE_TYPE: str = Field(default="minio", env="STORAGE_TYPE")  # local, minio, s3
    STORAGE_URL: str = Field(default="http://localhost:9000", env="STORAGE_URL")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", env="MINIO_SECRET_KEY")
    MINIO_BUCKET: str = Field(default="virtual-tryon", env="MINIO_BUCKET")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # File upload settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/jpg", "image/png", "image/bmp"]
    UPLOAD_DIR: str = "uploads"
    TEMP_DIR: str = "temp"
    
    # Processing settings
    MAX_CONCURRENT_JOBS: int = 5
    JOB_TIMEOUT: int = 600  # 10 minutes
    
    # Database settings (if needed later)
    DATABASE_URL: str = Field(default="sqlite:///./app.db", env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()