"""
=============================================================================
FaceForge - Module 2: Computer Vision & Face Detection (module2_detection.py)
Contributed by: Member 2 (Computer Vision & Face Framing)
Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur

Responsibilities of Member 2:
- Face detection using OpenCV Haar Cascade Classifier (Frontal + Profile faces)
- Multi-face bounding box extraction in (x, y, w, h) format
- Safe handling of image formats (uint8, float32, BGR, Grayscale)
- Multi-angle detection with horizontal flipping
- Returns clean list of bounding boxes (empty list [] if no face is detected)
=============================================================================
"""

import os
import threading
from typing import List, Tuple
import cv2
import numpy as np

_CASCADE_LOCK = threading.Lock()

# Locate cascade XML files: check local models/ directory first, then cv2 built-in data
BASE_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(BASE_DIR, "models")


def _get_cascade_path(filename: str) -> str:
    local_path = os.path.join(MODELS_DIR, filename)
    if os.path.exists(local_path):
        return local_path
    if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
        builtin_path = os.path.join(cv2.data.haarcascades, filename)
        if os.path.exists(builtin_path):
            return builtin_path
    return local_path


_FRONTAL_PATH = _get_cascade_path("haarcascade_frontalface_default.xml")
_PROFILE_PATH = _get_cascade_path("haarcascade_profileface.xml")

_frontal_cascade = None
_profile_cascade = None


def _load_cascades():
    global _frontal_cascade, _profile_cascade
    if _frontal_cascade is None and os.path.exists(_FRONTAL_PATH):
        try:
            _frontal_cascade = cv2.CascadeClassifier(_FRONTAL_PATH)
        except Exception as e:
            print(f"[Warning] Failed to load frontal cascade: {e}")

    if _profile_cascade is None and os.path.exists(_PROFILE_PATH):
        try:
            _profile_cascade = cv2.CascadeClassifier(_PROFILE_PATH)
        except Exception as e:
            print(f"[Warning] Failed to load profile cascade: {e}")


_load_cascades()


def _calculate_iou(b1: Tuple[int, int, int, int], b2: Tuple[int, int, int, int]) -> float:
    x1, y1, w1, h1 = b1
    x2, y2, w2, h2 = b2

    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)

    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    if inter_area <= 0:
        return 0.0

    b1_area = w1 * h1
    b2_area = w2 * h2
    union_area = float(b1_area + b2_area - inter_area)
    return inter_area / union_area if union_area > 0 else 0.0


def _apply_nms(boxes: List[Tuple[int, int, int, int]], iou_thresh: float = 0.35) -> List[Tuple[int, int, int, int]]:
    """Simple Non-Maximum Suppression to remove redundant overlapping boxes."""
    if not boxes:
        return []
    # Sort boxes by area descending (prefer larger bounding boxes)
    sorted_boxes = sorted(boxes, key=lambda b: b[2] * b[3], reverse=True)
    selected = []
    for box in sorted_boxes:
        overlap = False
        for chosen in selected:
            if _calculate_iou(box, chosen) > iou_thresh:
                overlap = True
                break
        if not overlap:
            selected.append(box)
    return selected


def find_faces(img: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detect all human faces in an image.

    Args:
        img: Input image as OpenCV NumPy ndarray (BGR, Grayscale, or BGRA format).
             Supports uint8, float32, float64 safely.

    Returns:
        List of (x, y, w, h) bounding box coordinates.
        Returns empty list [] if no face is detected. Never invents fake faces.
    """
    if img is None or not isinstance(img, np.ndarray) or img.size == 0:
        return []

    # Robust type handling: Handle float32/float64 safely
    if img.dtype in (np.float32, np.float64):
        # Check if values are in 0..1 range
        val_max = float(np.max(img)) if img.size > 0 else 0.0
        val_min = float(np.min(img)) if img.size > 0 else 0.0
        if val_max <= 1.05 and val_min >= -0.05:
            img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        else:
            img = np.clip(img, 0, 255).astype(np.uint8)
    elif img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)

    # Ensure memory is contiguous
    img = np.ascontiguousarray(img)

    # Convert to grayscale
    if img.ndim == 2:
        gray = img
    elif img.ndim == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif img.ndim == 3 and img.shape[2] == 4:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    else:
        return []

    h, w = gray.shape[:2]
    if h < 20 or w < 20:
        return []

    # High-resolution performance optimization:
    # Scale down for detection if image is larger than 960px on longest edge
    scale = 1.0
    max_dim = max(h, w)
    if max_dim > 960:
        scale = 960.0 / max_dim
        detect_gray = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    else:
        detect_gray = gray

    det_h, det_w = detect_gray.shape[:2]
    collected_boxes: List[Tuple[int, int, int, int]] = []

    with _CASCADE_LOCK:
        _load_cascades()

        # Step 1: Frontal Face Detection (high precision minNeighbors=6)
        if _frontal_cascade is not None and not _frontal_cascade.empty():
            try:
                frontal_faces = _frontal_cascade.detectMultiScale(
                    detect_gray,
                    scaleFactor=1.1,
                    minNeighbors=6,
                    minSize=(32, 32)
                )
                for (x, y, bw, bh) in frontal_faces:
                    collected_boxes.append((int(x), int(y), int(bw), int(bh)))
            except Exception as e:
                print(f"[Warning] Frontal face cascade error: {e}")

        # Step 2: Profile / Side-angle Face Detection if frontal found few or no faces
        if len(collected_boxes) == 0 and _profile_cascade is not None and not _profile_cascade.empty():
            try:
                # Profile facing right
                prof_right = _profile_cascade.detectMultiScale(
                    detect_gray,
                    scaleFactor=1.1,
                    minNeighbors=6,
                    minSize=(32, 32)
                )
                for (x, y, bw, bh) in prof_right:
                    collected_boxes.append((int(x), int(y), int(bw), int(bh)))

                # Horizontally flipped for profile facing left
                flipped_gray = cv2.flip(detect_gray, 1)
                prof_left = _profile_cascade.detectMultiScale(
                    flipped_gray,
                    scaleFactor=1.1,
                    minNeighbors=6,
                    minSize=(32, 32)
                )
                for (fx, fy, fbw, fbh) in prof_left:
                    # Invert x back to original coordinate space
                    orig_x = det_w - (fx + fbw)
                    collected_boxes.append((int(orig_x), int(fy), int(fbw), int(fbh)))
            except Exception as e:
                print(f"[Warning] Profile face cascade error: {e}")

    # Remove overlapping duplicate boxes with NMS
    filtered_boxes = _apply_nms(collected_boxes, iou_thresh=0.35)

    # Rescale bounding boxes back to original dimensions
    final_boxes: List[Tuple[int, int, int, int]] = []
    for (x, y, bw, bh) in filtered_boxes:
        if scale != 1.0:
            rx = int(round(x / scale))
            ry = int(round(y / scale))
            rw = int(round(bw / scale))
            rh = int(round(bh / scale))
        else:
            rx, ry, rw, rh = x, y, bw, bh

        # Clamping to image bounds
        rx = max(0, min(rx, w - 1))
        ry = max(0, min(ry, h - 1))
        rw = min(rw, w - rx)
        rh = min(rh, h - ry)

        if rw >= 20 and rh >= 20:
            final_boxes.append((rx, ry, rw, rh))

    return final_boxes
