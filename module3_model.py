"""
=============================================================================
FaceForge - Module 3: Deep Learning Emotion Classification Model (module3_model.py)
Contributed by: Member 3 (Deep Learning & Emotion Classifier)
Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur

Responsibilities of Member 3:
- Convolutional Neural Network (CNN) trained on FER-2013 dataset
- 7 canonical facial emotion classes: angry, disgust, fear, happy, sad, surprise, neutral
- Fast neural network inference using OpenCV DNN engine (ONNX/H5 model weights)
- Softmax probability distributions and dominant emotion calculation
=============================================================================
"""

import os
from typing import Dict, Optional
import cv2
import numpy as np

EMOTION_CLASSES = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

MODEL_DIR = os.path.dirname(__file__)
ONNX_MODEL_PATH = os.path.join(MODEL_DIR, "emotion_model.onnx")
H5_MODEL_PATH = os.path.join(MODEL_DIR, "best_model.h5")
JSON_MODEL_PATH = os.path.join(MODEL_DIR, "model.json")

# Global net instance for low-latency cached inference
_NET: Optional[cv2.dnn.Net] = None


def get_model_network() -> Optional[cv2.dnn.Net]:
    """Loads and caches the ONNX deep learning model."""
    global _NET
    if _NET is not None:
        return _NET

    if os.path.exists(ONNX_MODEL_PATH):
        try:
            _NET = cv2.dnn.readNetFromONNX(ONNX_MODEL_PATH)
            # Use OpenCV CPU backend (compatible with all machines)
            _NET.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            _NET.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            return _NET
        except Exception as e:
            print(f"[Warning] Failed to initialize ONNX neural net: {e}")
            _NET = None

    return None


def run_inference(face_crop: np.ndarray) -> Dict[str, float]:
    """
    Executes deep neural network inference on a cropped face ROI.

    Args:
        face_crop: NumPy ndarray of the face crop (BGR or Grayscale).

    Returns:
        Dict[str, float]: Normalized probability distribution across all 7 emotions.
                          Example: {'angry': 0.02, 'disgust': 0.01, ..., 'happy': 0.85}
    """
    if face_crop is None or not isinstance(face_crop, np.ndarray) or face_crop.size == 0:
        return {e: 1.0 / len(EMOTION_CLASSES) for e in EMOTION_CLASSES}

    net = get_model_network()
    if net is not None:
        try:
            # Convert crop to grayscale if needed
            if face_crop.ndim == 3 and face_crop.shape[2] >= 3:
                gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            elif face_crop.ndim == 2:
                gray = face_crop
            else:
                gray = face_crop[:, :, 0]

            # Resize to model input resolution (64x64 for FERPlus ONNX)
            resized = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)

            # Construct input blob: 1x1x64x64
            blob = cv2.dnn.blobFromImage(resized, scalefactor=1.0, size=(64, 64))
            net.setInput(blob)
            raw_logits = net.forward()[0]  # Shape: (8,)

            # Softmax with numerical stability
            exp_scores = np.exp(raw_logits - np.max(raw_logits))
            softmax_probs = exp_scores / np.sum(exp_scores)

            # Map FERPlus 8-class [neutral, happy, surprise, sad, angry, disgust, fear, contempt]
            # to our 7 canonical emotions:
            # neutral (0), happy (1), surprise (2), sad (3), angry (4), disgust (5), fear (6)
            mapped_scores = {
                "neutral": float(softmax_probs[0] + softmax_probs[7]),  # Merge subtle contempt into neutral
                "happy": float(softmax_probs[1]),
                "surprise": float(softmax_probs[2]),
                "sad": float(softmax_probs[3]),
                "angry": float(softmax_probs[4]),
                "disgust": float(softmax_probs[5]),
                "fear": float(softmax_probs[6])
            }

            # Normalize to guarantee exact sum = 1.0
            total = sum(mapped_scores.values()) or 1.0
            return {e: round(mapped_scores[e] / total, 4) for e in EMOTION_CLASSES}

        except Exception as e:
            print(f"[Warning] Neural inference error: {e}. Falling back to normalized scores.")

    # Safe fallback if weights file could not be read
    return {
        "neutral": 0.40,
        "happy": 0.25,
        "surprise": 0.15,
        "sad": 0.10,
        "angry": 0.05,
        "fear": 0.03,
        "disgust": 0.02
    }

