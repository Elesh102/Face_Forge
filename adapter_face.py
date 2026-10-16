"""
Face Forge - Adapter for Module 2: Face Detection & Framing
File: adapter_face.py

CONTRACT:
    - detect_faces(img) -> List of (x, y, w, h) bounding boxes.
    - crop_face(img, box) -> Face crop array (NumPy ndarray).
    - read_video(path, step) -> Generator yielding (frame_number, frame).

MOCK BEHAVIOR (TODAY):
    - detect_faces returns one fixed, centered box proportional to the frame size.
    - crop_face returns the sliced region using NumPy.
    - read_video uses OpenCV cv2.VideoCapture to sample frames every Nth step.

HOW TO PLUG IN THE REAL MODULE:
    1. Place teammate's face detection file (e.g. `module2_detection.py`) in this project.
    2. Import their face detector in `detect_faces()`.
    3. Ensure their detector returns a list of (x, y, w, h) bounding boxes.
    4. Enable `use_module2: true` in `config.yaml` or through the Settings UI.
"""

from typing import List, Tuple, Generator
import os
import cv2
import numpy as np

def detect_faces(
    img: np.ndarray,
    use_real: bool = False
) -> List[Tuple[int, int, int, int]]:
    """
    Detects faces in a BGR image.
    
    Args:
        img: np.ndarray in BGR color space.
        use_real: bool flag whether to use real Module 2.
        
    Returns:
        List of (x, y, w, h) bounding box coordinates.
    """
    if img is None or img.size == 0:
        return []

    h, w = img.shape[:2]

    if use_real:
        try:
            # Teammate plug-in point:
            # from module2_detection import find_faces
            # boxes = find_faces(img)
            # return boxes
            
            # Optional fallback attempt using OpenCV's built-in Haar Cascade if teammate provided none:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            if os.path.exists(cascade_path):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                face_cascade = cv2.CascadeClassifier(cascade_path)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
                if len(faces) > 0:
                    return [(int(x), int(y), int(bw), int(bh)) for (x, y, bw, bh) in faces]
            raise NotImplementedError("Module 2 face detection model file not provided.")
        except Exception as e:
            print(f"[Warning] Module 2 Face Detection unavailable: {e}. Falling back to mock centered box.")

    # Mock behavior: return a realistic centered box covering ~45% of image center
    box_w = max(40, int(w * 0.45))
    box_h = max(40, int(h * 0.50))
    x = max(0, int((w - box_w) / 2))
    y = max(0, int((h - box_h) / 3))

    # Ensure box stays within bounds
    box_w = min(box_w, w - x)
    box_h = min(box_h, h - y)

    return [(x, y, box_w, box_h)]

def crop_face(img: np.ndarray, box: Tuple[int, int, int, int]) -> np.ndarray:
    """
    Crops the face region from an image using the bounding box.
    
    Args:
        img: Source BGR image.
        box: (x, y, w, h) bounding box.
        
    Returns:
        NumPy crop array.
    """
    if img is None or img.size == 0:
        return np.zeros((1, 1, 3), dtype=np.uint8)

    x, y, w, h = box
    img_h, img_w = img.shape[:2]

    # Boundary protection
    x1 = max(0, min(x, img_w - 1))
    y1 = max(0, min(y, img_h - 1))
    x2 = max(x1 + 1, min(x + w, img_w))
    y2 = max(y1 + 1, min(y + h, img_h))

    crop = img[y1:y2, x1:x2]
    if crop.size == 0:
        return np.zeros((30, 30, 3), dtype=np.uint8)
    return crop

def read_video(video_path: str, step: int = 10) -> Generator[Tuple[int, np.ndarray], None, None]:
    """
    Reads a video file and yields sampled frames.
    
    Args:
        video_path: Path to MP4/AVI video file.
        step: Frame sampling interval (e.g. process every 10th frame).
        
    Yields:
        (frame_number, frame_ndarray)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[Error] Could not open video file: {video_path}")
        return

    frame_index = 0
    step = max(1, step)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_index % step == 0:
                yield frame_index, frame
            frame_index += 1
    finally:
        cap.release()
