import os
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    # Service configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Model configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "../../models/viton-hd")
    DEVICE: str = os.getenv("DEVICE", "cuda" if os.getenv("CUDA_VISIBLE_DEVICES") else "cpu")
    
    # Image processing
    IMAGE_SIZE: tuple = (512, 384)  # Width, Height for VITON-HD
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FORMATS: list = ["jpg", "jpeg", "png", "bmp"]
    
    # Temporary files
    TEMP_DIR: str = os.getenv("TEMP_DIR", "./temp")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()

# Ensure temp directory exists
Path(settings.TEMP_DIR).mkdir(parents=True, exist_ok=True)