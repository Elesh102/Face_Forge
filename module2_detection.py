"""
=============================================================================
FaceForge - Module 2: Computer Vision Face Detection (module2_detection.py)
Contributed by: Member 2 (Face Detection & Framing)
Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur

Detection Model: OpenCV YuNet (face_detection_yunet_2023mar.onnx)
Input: OpenCV image/frame (BGR NumPy ndarray)
Output: List of bounding boxes [(x, y, w, h), ...]

Responsibilities & Capabilities of Member 2:
1. Human face detection using OpenCV YuNet Deep Neural Network
2. Multi-pose face detection (Frontal, Profile, Upward, Downward angles)
3. Object-only false-positive rejection (returns [] on non-face scenes)
4. Safe input sanitization for float32, float64, uint8, Grayscale, and BGRA
5. Thread-safe concurrent execution (300 requests stable bounding boxes)
=============================================================================
"""

from typing import List, Tuple
from pathlib import Path
import threading

import cv2
import numpy as np


# ============================================================
# 1. CONFIGURATION
# ============================================================

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "face_detection_yunet_2023mar.onnx"
)

CONFIDENCE_THRESHOLD = 0.80
NMS_THRESHOLD = 0.30
TOP_K = 5000


# ============================================================
# 2. DETECTOR INITIALIZATION
# ============================================================

_detector = None
_detector_lock = threading.Lock()


def initialize_detector() -> None:
    """
    Load the YuNet model once.

    Call this during application startup if you want
    to detect missing model files before processing frames.
    """

    global _detector

    with _detector_lock:

        if _detector is not None:
            return

        if not MODEL_PATH.is_file():
            raise FileNotFoundError(
                f"YuNet model file not found: {MODEL_PATH}"
            )

        try:
            _detector = cv2.FaceDetectorYN.create(
                str(MODEL_PATH),
                "",
                (320, 320),
                CONFIDENCE_THRESHOLD,
                NMS_THRESHOLD,
                TOP_K
            )

        except cv2.error as error:
            raise RuntimeError(
                f"Unable to initialize YuNet model: {error}"
            ) from error

        if _detector is None:
            raise RuntimeError(
                "YuNet detector initialization failed."
            )


# ============================================================
# 3. INPUT IMAGE VALIDATION AND PREPROCESSING
# ============================================================

def _prepare_image(img: np.ndarray):
    """
    Validate and normalize an image.

    Accepted:
        - uint8 BGR image
        - uint8 grayscale image
        - uint8 BGRA image
        - float32 / float64 images in range [0, 1] or [0, 255]

    Returns:
        Valid BGR uint8 image, or None for invalid input.
    """

    if not isinstance(img, np.ndarray):
        return None

    if img.size == 0:
        return None

    if img.dtype not in (np.uint8, np.float32, np.float64):
        return None

    if img.dtype != np.uint8:

        if not np.isfinite(img).all():
            return None

        min_value = float(np.min(img))
        max_value = float(np.max(img))

        if min_value < 0 or max_value > 255:
            return None

        if max_value <= 1.0:
            img = img * 255.0

        img = np.clip(img, 0, 255).astype(np.uint8)

    # Grayscale -> BGR
    if img.ndim == 2:

        img = cv2.cvtColor(
            img,
            cv2.COLOR_GRAY2BGR
        )

    elif img.ndim == 3:

        channels = img.shape[2]

        # BGRA -> BGR
        if channels == 4:

            img = cv2.cvtColor(
                img,
                cv2.COLOR_BGRA2BGR
            )

        elif channels != 3:
            return None

    else:
        return None

    height, width = img.shape[:2]

    if height <= 0 or width <= 0:
        return None

    return np.ascontiguousarray(img)


# ============================================================
# 4. MAIN FACE DETECTION FUNCTION
# ============================================================

def find_faces(
    img: np.ndarray
) -> List[Tuple[int, int, int, int]]:
    """
    Detect all faces in the supplied image/frame.

    Parameters:
        img:
            OpenCV NumPy image in BGR format.

    Returns:
        A list of integer bounding boxes:

            [(x, y, w, h), ...]

        Returns an empty list if:
            - Input image is invalid.
            - No face is detected.

    Notes:
        - Works with still images.
        - Works with individual video frames.
        - Works with individual webcam frames.
        - Supports multiple faces.
        - Does not draw bounding boxes.
        - Does not read files or open a camera.
    """

    # Step 1: Validate image
    frame = _prepare_image(img)

    if frame is None:
        return []

    height, width = frame.shape[:2]

    # Step 2: Initialize detector if not already loaded
    initialize_detector()

    # Step 3: Run YuNet detection
    try:

        with _detector_lock:

            _detector.setInputSize((width, height))

            _, detected_faces = _detector.detect(frame)

    except cv2.error as error:

        raise RuntimeError(
            f"YuNet face detection failed: {error}"
        ) from error

    # Step 4: Handle no detections
    if detected_faces is None:
        return []

    bounding_boxes = []

    # Step 5: Extract and validate bounding boxes
    for face in detected_faces:

        x, y, box_width, box_height = face[:4]

        x1 = max(0, int(round(x)))
        y1 = max(0, int(round(y)))

        x2 = min(
            width,
            int(round(x + box_width))
        )

        y2 = min(
            height,
            int(round(y + box_height))
        )

        final_width = x2 - x1
        final_height = y2 - y1

        if final_width <= 0 or final_height <= 0:
            continue

        bounding_boxes.append(
            (
                x1,
                y1,
                final_width,
                final_height
            )
        )

    # Step 6: Consistent ordering
    bounding_boxes.sort(
        key=lambda box: (box[1], box[0])
    )

    return bounding_boxes


# ============================================================
# 5. MODEL INFORMATION
# ============================================================

def get_detector_info() -> dict:
    """
    Return detector configuration information.
    """

    return {
        "model": "YuNet",
        "model_file": MODEL_PATH.name,
        "model_exists": MODEL_PATH.is_file(),
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "nms_threshold": NMS_THRESHOLD,
        "opencv_version": cv2.__version__
    }
