"""
adapter_face.py — Adapter for Module 2: Face Detection & Video/Webcam Frames
=============================================================================

ROLE IN FACE FORGE:
Acts as the bridge between Module 4 and Module 2 (OpenCV face detection,
bounding box localization, and frame slicing from video files and live webcam).

HOW TO REPLACE THIS MOCK WITH REAL TEAMMATE CODE:
1. Place Teammate 2's face detector file (e.g. `haar_detector.py` or `dnn_face.py`) into the project.
2. In this file, import their detector function:
       from haar_detector import detect_all_faces
3. In `detect_faces(img, config=None)`, replace the mock return with:
       boxes = detect_all_faces(img)
       return boxes  # List of tuples: [(x, y, w, h), ...]
4. Enable `use_module2: true` in `config.yaml` or via the Settings page.
5. If the real detector fails or is missing, this adapter gracefully catches the error
   and falls back to the default centered mock box without crashing.
"""

import logging
from typing import List, Tuple, Generator
import cv2
import numpy as np

logger = logging.getLogger(__name__)

MODULE2_WARNING = None


def detect_faces(img: np.ndarray, config: dict = None) -> List[Tuple[int, int, int, int]]:
    """
    Detect bounding boxes of faces present in the input image.

    Args:
        img: np.ndarray image matrix (H, W, C).
        config: Optional dict containing configuration settings.

    Returns:
        List of bounding boxes in format: [(x, y, w, h), ...]
    """
    global MODULE2_WARNING
    MODULE2_WARNING = None

    use_real = config.get("use_module2", False) if config else False

    if use_real:
        try:
            # TEAMMATE INTEGRATION POINT (Module 2):
            # from teammate_module2 import run_face_detection
            # return run_face_detection(img)
            raise ImportError("Teammate's Module 2 file not detected in project.")
        except Exception as e:
            MODULE2_WARNING = f"Module 2 real adapter unavailable ({str(e)}). Falling back to mock face detector."
            logger.warning(MODULE2_WARNING)

    # Mock implementation: returns one fixed centered bounding box
    if img is None:
        return []

    h, w = img.shape[:2]
    # Fixed centered box: 40% of width and height in the center
    box_w = max(10, int(w * 0.45))
    box_h = max(10, int(h * 0.50))
    box_x = max(0, int((w - box_w) / 2))
    box_y = max(0, int((h - box_h) / 2))

    return [(box_x, box_y, box_w, box_h)]


def crop_face(img: np.ndarray, box: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Crop a face region from the image using NumPy slicing.

    Args:
        img: np.ndarray image.
        box: (x, y, w, h) bounding box.

    Returns:
        np.ndarray: Cropped face image.
    """
    if img is None:
        return np.zeros((48, 48, 3), dtype=np.uint8)

    x, y, w, h = box
    img_h, img_w = img.shape[:2]

    # Boundary check to prevent negative index or out of bounds slicing
    x1 = max(0, min(x, img_w - 1))
    y1 = max(0, min(y, img_h - 1))
    x2 = max(x1 + 1, min(x + w, img_w))
    y2 = max(y1 + 1, min(y + h, img_h))

    cropped = img[y1:y2, x1:x2]
    if cropped.size == 0:
        return np.zeros((48, 48, 3), dtype=np.uint8)

    return cropped


def read_video(video_path: str, step: int = 10) -> Generator[Tuple[int, np.ndarray], None, None]:
    """
    Yields (frame_number, frame) from an input video file using OpenCV.
    Samples every `step`-th frame.

    Args:
        video_path: Path to video file (MP4, AVI, etc.)
        step: Sampling interval (e.g., step=10 processes frames 0, 10, 20...)

    Yields:
        (frame_number: int, frame: np.ndarray)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return

    frame_idx = 0
    step = max(1, step)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % step == 0:
                yield (frame_idx, frame)

            frame_idx += 1
    finally:
        cap.release()


def get_video_total_frames(video_path: str) -> int:
    """Returns total frame count of a video file."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return total


def get_warning():
    """Returns the latest warning string if Module 2 failed to load, else None."""
    return MODULE2_WARNING
