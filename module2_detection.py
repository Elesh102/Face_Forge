from typing import List, Tuple

import cv2
import numpy as np


# Load pre-trained Haar Cascade face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

if face_cascade.empty():
    raise IOError("Unable to load Haar Cascade XML file")


def find_faces(img: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detect all human faces in an image.

    Args:
        img: Input image as OpenCV NumPy ndarray (BGR format).

    Returns:
        List of (x, y, w, h) bounding box coordinates.
        Returns [] if no face is detected.
    """

    # Validate input
    if not isinstance(img, np.ndarray) or img.size == 0:
        return []

    # Robust type handling: Handle float32/float64/int32 safely
    if img.dtype in (np.float32, np.float64):
        val_max = float(np.max(img)) if img.size > 0 else 0.0
        val_min = float(np.min(img)) if img.size > 0 else 0.0
        if val_max <= 1.05 and val_min >= -0.05:
            img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        else:
            img = np.clip(img, 0, 255).astype(np.uint8)
    elif img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)

    img = np.ascontiguousarray(img)

    # Check image dimensions
    if img.ndim == 2:
        gray = img

    elif img.ndim == 3 and img.shape[2] == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    elif img.ndim == 3 and img.shape[2] == 4:
        gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

    else:
        return []

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Return bounding box coordinates
    return [
        (int(x), int(y), int(w), int(h))
        for (x, y, w, h) in faces
    ]
