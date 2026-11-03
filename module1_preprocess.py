"""
=============================================================================
FaceForge - Module 1: Dataset & Image Preprocessing Pipeline
Contributed by: Member 1 (Dataset Collection & Image Preprocessing)
Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur

Responsibilities of Member 1:
- Handling the FER-2013 facial expression dataset (48x48 grayscale images)
- CLAHE (Contrast Limited Adaptive Histogram Equalization) for lighting adjustment
- Cropping and resizing face images to 48x48 pixels for CNN model input
- Standardizing FER-2013 canonical emotion label index mapping (0 to 6)
=============================================================================
"""

from typing import Tuple, Dict
import cv2
import numpy as np

# Standard FER-2013 Ground Truth Emotion Labels mapped by Member 1
# Reference: Kaggle FER-2013 Dataset Ground Truth
EMOTION_LABELS: Dict[int, str] = {
    0: "Angry",
    1: "Disgust",
    2: "Fear",
    3: "Happy",
    4: "Sad",
    5: "Surprise",
    6: "Neutral"
}


def preprocess_image(img: np.ndarray) -> np.ndarray:
    """
    Preprocesses an input image frame:
    Enhances contrast using CLAHE and normalizes lighting conditions.

    Args:
        img: Input image as OpenCV NumPy ndarray (BGR format).

    Returns:
        np.ndarray: Preprocessed image in BGR format ready for face detection.
    """
    if img is None or not isinstance(img, np.ndarray) or img.size == 0:
        return img

    try:
        # Check channels
        if img.ndim == 3 and img.shape[2] == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif img.ndim == 3 and img.shape[2] == 4:
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        elif img.ndim == 2:
            gray = img
        else:
            return img

        # Apply CLAHE to balance contrast and lighting
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Convert back to 3-channel BGR for downstream detector compatibility
        return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    except Exception as e:
        print(f"[Warning] module1_preprocess failed: {e}. Returning original image.")
        return img


def prepare_face_crop_for_model(face_crop: np.ndarray, target_size: Tuple[int, int] = (48, 48)) -> np.ndarray:
    """
    Resizes and formats a cropped face ROI to the exact input shape required
    by the FER-2013 CNN model (48, 48, 1).

    Args:
        face_crop: Cropped face image (BGR or Grayscale).
        target_size: Target tuple (default (48, 48)).

    Returns:
        np.ndarray: Normalized float32 array shaped (1, 48, 48, 1).
    """
    if face_crop is None or face_crop.size == 0:
        return np.zeros((1, target_size[0], target_size[1], 1), dtype=np.float32)

    if face_crop.ndim == 3 and face_crop.shape[2] >= 3:
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    else:
        gray = face_crop

    resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA)
    norm = resized.astype("float32") / 255.0
    return np.expand_dims(norm, axis=(0, -1))
