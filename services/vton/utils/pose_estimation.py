import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
from typing import Dict, List, Tuple, Any
from loguru import logger
import asyncio

from config import settings

class PoseEstimator:
    """Human pose estimation using MediaPipe"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        
        # COCO-style keypoint mapping for VITON compatibility
        self.keypoint_mapping = {
            'nose': 0,
            'left_eye': 1,
            'right_eye': 2,
            'left_ear': 3,
            'right_ear': 4,
            'left_shoulder': 5,
            'right_shoulder': 6,
            'left_elbow': 7,
            'right_elbow': 8,
            'left_wrist': 9,
            'right_wrist': 10,
            'left_hip': 11,
            'right_hip': 12,
            'left_knee': 13,
            'right_knee': 14,
            'left_ankle': 15,
            'right_ankle': 16,
            'neck': 17  # Computed as midpoint of shoulders
        }
    
    async def estimate_pose(self, image_path: Path) -> Dict[str, Any]:
        """
        Estimate human pose from image
        
        Args:
            image_path: Path to person image
            
        Returns:
            Dictionary containing pose data
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image
            results = self.pose.process(rgb_image)
            
            if not results.pose_landmarks:
                logger.warning("No pose detected in image")
                return self._create_empty_pose_data()
            
            # Extract keypoints
            keypoints = self._extract_keypoints(results.pose_landmarks, image.shape)
            
            # Create pose data
            pose_data = {
                'keypoints': keypoints,
                'bbox': self._compute_bbox(keypoints),
                'segmentation': self._extract_segmentation(results.segmentation_mask, image.shape) if results.segmentation_mask else None,
                'confidence': self._compute_overall_confidence(keypoints),
                'image_shape': image.shape[:2]  # (height, width)
            }
            
            logger.debug(f"Pose estimation completed with {len(keypoints)} keypoints")
            return pose_data
            
        except Exception as e:
            logger.error(f"Pose estimation failed: {e}")
            return self._create_empty_pose_data()
    
    def _extract_keypoints(self, landmarks, image_shape: Tuple[int, int, int]) -> List[Tuple[float, float, float]]:
        """
        Extract keypoints from MediaPipe landmarks
        
        Args:
            landmarks: MediaPipe pose landmarks
            image_shape: Shape of input image (H, W, C)
            
        Returns:
            List of keypoints as (x, y, confidence) normalized to [0, 1]
        """
        h, w = image_shape[:2]
        keypoints = []
        
        # Map MediaPipe landmarks to COCO format
        mp_to_coco = {
            0: self.mp_pose.PoseLandmark.NOSE,
            1: self.mp_pose.PoseLandmark.LEFT_EYE,
            2: self.mp_pose.PoseLandmark.RIGHT_EYE,
            3: self.mp_pose.PoseLandmark.LEFT_EAR,
            4: self.mp_pose.PoseLandmark.RIGHT_EAR,
            5: self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            6: self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            7: self.mp_pose.PoseLandmark.LEFT_ELBOW,
            8: self.mp_pose.PoseLandmark.RIGHT_ELBOW,
            9: self.mp_pose.PoseLandmark.LEFT_WRIST,
            10: self.mp_pose.PoseLandmark.RIGHT_WRIST,
            11: self.mp_pose.PoseLandmark.LEFT_HIP,
            12: self.mp_pose.PoseLandmark.RIGHT_HIP,
            13: self.mp_pose.PoseLandmark.LEFT_KNEE,
            14: self.mp_pose.PoseLandmark.RIGHT_KNEE,
            15: self.mp_pose.PoseLandmark.LEFT_ANKLE,
            16: self.mp_pose.PoseLandmark.RIGHT_ANKLE,
        }
        
        # Extract first 17 keypoints
        for i in range(17):
            if i in mp_to_coco:
                landmark = landmarks.landmark[mp_to_coco[i]]
                # MediaPipe coordinates are already normalized
                keypoints.append((landmark.x, landmark.y, landmark.visibility))
            else:
                keypoints.append((0.0, 0.0, 0.0))
        
        # Compute neck as midpoint of shoulders (keypoint 17)
        if len(keypoints) >= 6:
            left_shoulder = keypoints[5]
            right_shoulder = keypoints[6]
            if left_shoulder[2] > 0.5 and right_shoulder[2] > 0.5:
                neck_x = (left_shoulder[0] + right_shoulder[0]) / 2
                neck_y = (left_shoulder[1] + right_shoulder[1]) / 2
                neck_conf = min(left_shoulder[2], right_shoulder[2])
                keypoints.append((neck_x, neck_y, neck_conf))
            else:
                keypoints.append((0.0, 0.0, 0.0))
        
        return keypoints
    
    def _compute_bbox(self, keypoints: List[Tuple[float, float, float]]) -> Tuple[float, float, float, float]:
        """
        Compute bounding box from keypoints
        
        Args:
            keypoints: List of keypoints as (x, y, confidence)
            
        Returns:
            Bounding box as (x_min, y_min, width, height) in normalized coordinates
        """
        valid_points = [(x, y) for x, y, conf in keypoints if conf > 0.1]
        
        if not valid_points:
            return (0.0, 0.0, 1.0, 1.0)
        
        xs, ys = zip(*valid_points)
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        
        # Add padding
        padding = 0.1
        width = x_max - x_min
        height = y_max - y_min
        
        x_min = max(0.0, x_min - padding * width)
        y_min = max(0.0, y_min - padding * height)
        width = min(1.0 - x_min, width + 2 * padding * width)
        height = min(1.0 - y_min, height + 2 * padding * height)
        
        return (x_min, y_min, width, height)
    
    def _extract_segmentation(self, segmentation_mask, image_shape: Tuple[int, int, int]) -> np.ndarray:
        """
        Extract person segmentation mask
        
        Args:
            segmentation_mask: MediaPipe segmentation mask
            image_shape: Shape of input image
            
        Returns:
            Binary segmentation mask
        """
        if segmentation_mask is None:
            return np.zeros(image_shape[:2], dtype=np.uint8)
        
        # Convert to binary mask
        mask = (segmentation_mask > 0.5).astype(np.uint8) * 255
        
        return mask
    
    def _compute_overall_confidence(self, keypoints: List[Tuple[float, float, float]]) -> float:
        """
        Compute overall pose confidence
        
        Args:
            keypoints: List of keypoints with confidence scores
            
        Returns:
            Overall confidence score [0, 1]
        """
        confidences = [conf for _, _, conf in keypoints if conf > 0]
        return np.mean(confidences) if confidences else 0.0
    
    def _create_empty_pose_data(self) -> Dict[str, Any]:
        """Create empty pose data structure"""
        return {
            'keypoints': [(0.0, 0.0, 0.0)] * 18,
            'bbox': (0.0, 0.0, 1.0, 1.0),
            'segmentation': None,
            'confidence': 0.0,
            'image_shape': (512, 384)
        }
    
    async def visualize_pose(self, image_path: Path, pose_data: Dict[str, Any], output_path: Path) -> None:
        """
        Visualize pose estimation results
        
        Args:
            image_path: Path to input image
            pose_data: Pose estimation results
            output_path: Path to save visualization
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                return
            
            # Draw keypoints
            keypoints = pose_data['keypoints']
            h, w = image.shape[:2]
            
            for i, (x, y, conf) in enumerate(keypoints):
                if conf > 0.5:
                    px, py = int(x * w), int(y * h)
                    cv2.circle(image, (px, py), 3, (0, 255, 0), -1)
                    cv2.putText(image, str(i), (px + 5, py), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
            
            # Draw bounding box
            bbox = pose_data['bbox']
            x_min, y_min, width, height = bbox
            pt1 = (int(x_min * w), int(y_min * h))
            pt2 = (int((x_min + width) * w), int((y_min + height) * h))
            cv2.rectangle(image, pt1, pt2, (255, 0, 0), 2)
            
            # Save visualization
            cv2.imwrite(str(output_path), image)
            logger.debug(f"Pose visualization saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to visualize pose: {e}")