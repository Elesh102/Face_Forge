"""
adapter_emotion.py — Adapter for Module 3: Pretrained FER Emotion Model & Evaluation
=====================================================================================

ROLE IN FACE FORGE:
Acts as the bridge between Module 4 and Module 3 (FER-2013 7-class emotion model,
probability score generation, and model evaluation metrics).

HOW TO REPLACE THIS MOCK WITH REAL TEAMMATE CODE:
1. Place Teammate 3's PyTorch/Keras/ONNX model weights and inference file in the project.
2. In this file, import their model loading and prediction functions:
       from emotion_model import load_fer_model, predict_emotion_scores
3. In `predict_face(face_img, config=None)`, pass the cropped face image into their model:
       raw_scores = predict_emotion_scores(face_img)  # dict of 7 probabilities
4. Enable `use_module3: true` in `config.yaml` or through the Settings page.
5. If the real model fails to load, this adapter automatically logs a warning,
   falls back to valid simulated probabilities, and preserves system uptime.
"""

import logging
import random
from typing import Dict, Tuple, Any
import numpy as np

logger = logging.getLogger(__name__)

MODULE3_WARNING = None

# The exact 7 canonical emotion classes
EMOTION_CLASSES = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


def map_status(emotion: str, confidence: float, threshold: float = 0.50) -> str:
    """
    Map an emotion and confidence level to a human-readable system status.

    Rules:
      - confidence below threshold -> 'Uncertain'
      - happy -> 'Happy'
      - neutral, surprise -> 'Neutral'
      - sad, angry, fear, disgust -> 'Needs attention'
    """
    if confidence < threshold:
        return "Uncertain"

    emo = emotion.lower().strip()
    if emo == "happy":
        return "Happy"
    elif emo in ("neutral", "surprise"):
        return "Neutral"
    elif emo in ("sad", "angry", "fear", "disgust"):
        return "Needs attention"
    else:
        return "Neutral"


def _generate_mock_scores() -> Dict[str, float]:
    """Generates random but valid probabilities for the 7 emotion classes that sum to 1.0."""
    # Pick a dominant emotion to make predictions look natural
    dominant = random.choice(EMOTION_CLASSES)
    weights = {}
    for emo in EMOTION_CLASSES:
        if emo == dominant:
            weights[emo] = random.uniform(0.55, 0.95)
        else:
            weights[emo] = random.uniform(0.01, 0.15)

    total = sum(weights.values())
    scores = {emo: round(val / total, 4) for emo, val in weights.items()}

    # Ensure exact sum of 1.0 by adjusting the dominant score
    diff = 1.0 - sum(scores.values())
    scores[dominant] = round(scores[dominant] + diff, 4)

    return scores


def predict_face(face_img: np.ndarray, config: dict = None) -> Tuple[Dict[str, float], str, float, str]:
    """
    Run emotion classification on a cropped face image.

    Args:
        face_img: Cropped face image (np.ndarray).
        config: Optional configuration dictionary.

    Returns:
        tuple: (scores, dominant_emotion, confidence, status)
    """
    global MODULE3_WARNING
    MODULE3_WARNING = None

    threshold = config.get("confidence_threshold", 0.50) if config else 0.50
    use_real = config.get("use_module3", False) if config else False

    if use_real:
        try:
            # TEAMMATE INTEGRATION POINT (Module 3):
            # from teammate_module3 import run_fer_inference
            # scores = run_fer_inference(face_img)
            raise ImportError("Teammate's Module 3 model weights not detected in project.")
        except Exception as e:
            MODULE3_WARNING = f"Module 3 real adapter unavailable ({str(e)}). Falling back to mock emotion predictions."
            logger.warning(MODULE3_WARNING)

    # Mock implementation: generate valid probability distribution
    scores = _generate_mock_scores()
    dominant_emotion = max(scores, key=scores.get)
    confidence = float(scores[dominant_emotion])
    status = map_status(dominant_emotion, confidence, threshold)

    return scores, dominant_emotion, confidence, status


def predict_frame(frame: np.ndarray, box: Tuple[int, int, int, int], config: dict = None, face_idx: int = 0) -> Dict[str, Any]:
    """
    Process a single face in a frame and produce an official Face Forge RESULT RECORD.

    Result record fields:
      - face_index: int
      - box: (x, y, w, h)
      - scores: dict of 7 floats (angry, disgust, fear, happy, sad, surprise, neutral)
      - emotion: str
      - confidence: float
      - status: str (Happy / Neutral / Needs attention / Uncertain)
      - face_found: bool
    """
    if frame is None or box is None:
        return {
            "face_index": face_idx,
            "box": (0, 0, 0, 0),
            "scores": {emo: 0.0 for emo in EMOTION_CLASSES},
            "emotion": "None",
            "confidence": 0.0,
            "status": "Uncertain",
            "face_found": False
        }

    # Import crop_face from adapter_face
    from adapters.adapter_face import crop_face
    face_img = crop_face(frame, box)

    scores, emotion, confidence, status = predict_face(face_img, config)

    return {
        "face_index": face_idx,
        "box": box,
        "scores": scores,
        "emotion": emotion,
        "confidence": confidence,
        "status": status,
        "face_found": True
    }


def get_warning():
    """Returns the latest warning string if Module 3 failed to load, else None."""
    return MODULE3_WARNING
