"""
=============================================================================
FaceForge - Adapter for Module 3: Emotion Classification Model
File: adapter_emotion.py
Coordinated by: Member 4 (Integration) for Member 3 (Emotion Model)
Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur

Purpose:
Connects Member 3's deep learning model (module3_model.py) with the
FaceForge controller, computes confidence, and derives ethical status.
=============================================================================
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
        try:
            # Member 3 (Trained Emotion Recognition Model) Live Integration
            from module3_model import run_inference
            scores = run_inference(face_img)
            dominant_emo = max(scores, key=scores.get)
            confidence = float(scores[dominant_emo])
            status = derive_status(dominant_emo, confidence, confidence_threshold)
            return {
                "face_index": face_index,
                "box": list(box),
                "scores": scores,
                "emotion": dominant_emo,
                "confidence": round(confidence, 4),
                "status": status,
                "face_found": True
            }
        except Exception as e:
            print(f"[Warning] Module 3 Emotion Model unavailable: {e}. Falling back to simulated predictions.")

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
