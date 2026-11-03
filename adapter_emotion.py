"""
Face Forge - Adapter for Module 3: Emotion Classification Model
File: adapter_emotion.py

CONTRACT (Result Record):
    - face_index: int
    - box: (x, y, w, h)
    - scores: dict of 7 floats: {"angry": float, "disgust": float, "fear": float,
                                 "happy": float, "sad": float, "surprise": float, "neutral": float}
    - emotion: str (dominant emotion with highest score)
    - confidence: float (0.0 to 1.0)
    - status: str ("Happy", "Neutral", "Needs attention", "Uncertain")
    - face_found: bool

MOCK BEHAVIOR (TODAY):
    Generates realistic, normalized probability distributions over the 7 emotion classes
    that sum to 1.0. Calculates dominant emotion and sets the wellbeing status based on
    the project specification and confidence threshold.

HOW TO PLUG IN THE REAL MODULE:
    1. Place teammate's emotion classifier (e.g. `module3_model.py` and weights `.h5`/`.pt`) here.
    2. Import their inference function in `predict_face()`.
    3. Ensure their function returns scores for the 7 emotion classes.
    4. Enable `use_module3: true` in `config.yaml` or through the Settings UI.
"""

from typing import Dict, Any, List, Tuple
import random
import numpy as np

EMOTION_CLASSES = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

def derive_status(emotion: str, confidence: float, threshold: float = 0.50) -> str:
    """
    Derives the ethical wellbeing status from the detected facial expression.
    - If confidence is below threshold -> 'Uncertain'
    - 'happy' -> 'Happy'
    - 'neutral', 'surprise' -> 'Neutral'
    - 'sad', 'angry', 'fear', 'disgust' -> 'Needs attention'
    """
    if confidence < threshold:
        return "Uncertain"
    
    emotion = emotion.lower()
    if emotion == "happy":
        return "Happy"
    elif emotion in ["neutral", "surprise"]:
        return "Neutral"
    elif emotion in ["sad", "angry", "fear", "disgust"]:
        return "Needs attention"
    return "Uncertain"

def predict_face(
    face_img: np.ndarray,
    box: Tuple[int, int, int, int] = (0, 0, 0, 0),
    face_index: int = 0,
    confidence_threshold: float = 0.50,
    use_real: bool = False
) -> Dict[str, Any]:
    """
    Predicts emotion distribution for a single cropped face.
    """
    if face_img is None or face_img.size == 0:
        return {
            "face_index": face_index,
            "box": list(box),
            "scores": {e: 0.0 for e in EMOTION_CLASSES},
            "emotion": "neutral",
            "confidence": 0.0,
            "status": "Uncertain",
            "face_found": False
        }

    if use_real:
        # Module 3: pretrained FER model (module3/module3_model.py)
        try:
            from module3.module3_model import predict_emotion
            scores = predict_emotion(face_img)
        except Exception as e:
            # Live mode: report the failure, never show random emotions
            print(f"[Warning] Module 3 Emotion Model failed: {e}")
            return {
                "face_index": int(face_index),
                "box": [int(v) for v in box],
                "scores": {emo: 0.0 for emo in EMOTION_CLASSES},
                "emotion": "unknown",
                "confidence": 0.0,
                "status": "Uncertain",
                "face_found": False,
                "error": str(e)
            }
        dominant_emo = max(scores, key=scores.get)
        confidence = float(scores[dominant_emo])
        return {
            "face_index": int(face_index),
            "box": [int(v) for v in box],
            "scores": scores,
            "emotion": dominant_emo,
            "confidence": confidence,
            "status": derive_status(dominant_emo, confidence, confidence_threshold),
            "face_found": True
        }

    # Mock behavior: pick a dominant emotion and generate softmax-like scores
    dominant = random.choice(EMOTION_CLASSES)
    
    # Generate random positive weights with a peak at dominant
    raw_weights = {}
    for emo in EMOTION_CLASSES:
        if emo == dominant:
            raw_weights[emo] = random.uniform(2.5, 5.0)
        else:
            raw_weights[emo] = random.uniform(0.1, 1.2)
            
    total = sum(raw_weights.values())
    scores = {emo: round(val / total, 4) for emo, val in raw_weights.items()}
    
    # Re-normalize to ensure sum is exactly 1.0
    dominant_emo = max(scores, key=scores.get)
    confidence = scores[dominant_emo]
    status = derive_status(dominant_emo, confidence, confidence_threshold)

    return {
        "face_index": int(face_index),
        "box": [int(v) for v in box],
        "scores": scores,
        "emotion": dominant_emo,
        "confidence": float(confidence),
        "status": status,
        "face_found": True
    }

def predict_frame(
    frame: np.ndarray,
    confidence_threshold: float = 0.50,
    use_real: bool = False
) -> List[Dict[str, Any]]:
    """
    Combined frame-level prediction. Returns list of Result Records for detected faces.
    """
    if frame is None or frame.size == 0:
        return []

    h, w = frame.shape[:2]
    # Default centered box for single face mock
    box = (int(w * 0.25), int(h * 0.2), int(w * 0.5), int(h * 0.5))
    record = predict_face(
        face_img=frame,
        box=box,
        face_index=0,
        confidence_threshold=confidence_threshold,
        use_real=use_real
    )
    return [record]
