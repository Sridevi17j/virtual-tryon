import cv2
import numpy as np
from PIL import Image
import torch
from pathlib import Path
from typing import Tuple, Optional
from loguru import logger
import asyncio

from config import settings

class ImageProcessor:
    """Image preprocessing utilities for VITON-HD"""
    
    def __init__(self):
        self.target_size = settings.IMAGE_SIZE  # (width, height)
        
    async def preprocess_person(self, image_path: Path) -> np.ndarray:
        """
        Preprocess person image for virtual try-on
        
        Args:
            image_path: Path to person image
            
        Returns:
            Preprocessed image as numpy array (H, W, 3)
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize to target size
            image = cv2.resize(image, self.target_size, interpolation=cv2.INTER_LANCZOS4)
            
            # Normalize to [0, 255] uint8
            image = np.clip(image, 0, 255).astype(np.uint8)
            
            logger.debug(f"Preprocessed person image: {image.shape}")
            return image
            
        except Exception as e:
            logger.error(f"Failed to preprocess person image: {e}")
            raise
    
    async def preprocess_garment(self, image_path: Path) -> np.ndarray:
        """
        Preprocess garment image for virtual try-on
        
        Args:
            image_path: Path to garment image
            
        Returns:
            Preprocessed image as numpy array (H, W, 3)
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Remove background (simple method - can be improved)
            image = await self._remove_background(image)
            
            # Resize to target size
            image = cv2.resize(image, self.target_size, interpolation=cv2.INTER_LANCZOS4)
            
            # Normalize to [0, 255] uint8
            image = np.clip(image, 0, 255).astype(np.uint8)
            
            logger.debug(f"Preprocessed garment image: {image.shape}")
            return image
            
        except Exception as e:
            logger.error(f"Failed to preprocess garment image: {e}")
            raise
    
    async def _remove_background(self, image: np.ndarray) -> np.ndarray:
        """
        Simple background removal for garment images
        
        Args:
            image: Input image (H, W, 3)
            
        Returns:
            Image with background removed
        """
        try:
            # Convert to grayscale for thresholding
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Apply Otsu's thresholding
            _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Apply morphological operations to clean up mask
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Find contours and keep largest one
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                mask = np.zeros_like(mask)
                cv2.fillPoly(mask, [largest_contour], 255)
            
            # Apply mask to image
            result = image.copy()
            result[mask == 0] = [255, 255, 255]  # White background
            
            return result
            
        except Exception as e:
            logger.warning(f"Background removal failed, using original image: {e}")
            return image
    
    async def save_result(self, image: np.ndarray, output_path: Path) -> None:
        """
        Save processed image to file
        
        Args:
            image: Image array (H, W, 3)
            output_path: Output file path
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert RGB to BGR for OpenCV
            if len(image.shape) == 3:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image
            
            # Save image
            success = cv2.imwrite(str(output_path), image_bgr)
            if not success:
                raise ValueError(f"Failed to save image to {output_path}")
            
            logger.debug(f"Saved image to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise
    
    def resize_with_padding(self, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """
        Resize image with padding to maintain aspect ratio
        
        Args:
            image: Input image (H, W, 3)
            target_size: Target size (width, height)
            
        Returns:
            Resized image with padding
        """
        h, w = image.shape[:2]
        target_w, target_h = target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Create padded image
        padded = np.full((target_h, target_w, 3), 255, dtype=np.uint8)
        
        # Calculate padding
        pad_x = (target_w - new_w) // 2
        pad_y = (target_h - new_h) // 2
        
        # Place resized image in center
        padded[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized
        
        return padded
    
    def validate_image(self, image_path: Path) -> bool:
        """
        Validate if file is a valid image
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if valid image, False otherwise
        """
        try:
            # Check file extension
            if image_path.suffix.lower().lstrip('.') not in settings.SUPPORTED_FORMATS:
                return False
            
            # Try to load image
            image = cv2.imread(str(image_path))
            return image is not None
            
        except Exception:
            return False