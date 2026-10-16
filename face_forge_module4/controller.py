"""
controller.py — Pipeline Orchestrator for Face Forge Module 4
=============================================================

Routes each processing mode (Image, Video, Live Webcam) through the adapter pipeline:
  [Raw Input] -> Module 1 (adapter_preprocess) -> Module 2 (adapter_face) -> Module 3 (adapter_emotion) -> Storage

Manages configuration parameters and warning aggregation.
"""

import os
import io
import base64
import yaml
import cv2
import numpy as np
from PIL import Image

import storage
from adapters import adapter_preprocess, adapter_face, adapter_emotion

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

DEFAULT_CONFIG = {
    "demo_mode": True,
    "use_module1": False,
    "use_module2": False,
    "use_module3": False,
    "confidence_threshold": 0.50,
    "video_sampling_step": 10
}


def load_config() -> dict:
    """Load config.yaml, or return defaults if not found."""
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            if not isinstance(cfg, dict):
                return dict(DEFAULT_CONFIG)
            # Ensure all keys exist
            merged = dict(DEFAULT_CONFIG)
            merged.update(cfg)
            return merged
    except Exception as e:
        print(f"Error reading config.yaml: {e}")
        return dict(DEFAULT_CONFIG)


def save_config(new_config: dict) -> bool:
    """Save updated parameters to config.yaml."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        print(f"Error saving config.yaml: {e}")
        return False


def get_active_warnings() -> list:
    """Collect any fallback warnings from all three adapters."""
    warnings = []
    w1 = adapter_preprocess.get_warning()
    w2 = adapter_face.get_warning()
    w3 = adapter_emotion.get_warning()

    if w1:
        warnings.append(w1)
    if w2:
        warnings.append(w2)
    if w3:
        warnings.append(w3)

    return warnings


def get_badge_info() -> dict:
    """Returns badge text and CSS class depending on demo_mode."""
    cfg = load_config()
    is_demo = cfg.get("demo_mode", True)
    if is_demo:
        return {"text": "Demo data", "class": "badge-demo"}
    else:
        return {"text": "Live module", "class": "badge-live"}


def draw_detection_overlay(img_bgr: np.ndarray, records: list) -> np.ndarray:
    """
    Draw bounding boxes, emotion labels, and status tags on the image.
    Uses clean styling with clear contrast.
    """
    canvas = img_bgr.copy()

    for rec in records:
        box = rec.get("box", (0, 0, 0, 0))
        x, y, w, h = box
        emotion = rec.get("emotion", "Unknown")
        confidence = rec.get("confidence", 0.0)
        status = rec.get("status", "Neutral")

        # Color based on status
        if status == "Happy":
            color = (50, 205, 50)     # Lime Green
        elif status == "Neutral":
            color = (255, 191, 0)     # Amber/Sky
        elif status == "Needs attention":
            color = (60, 60, 255)     # Red
        else:
            color = (180, 180, 180)   # Gray for Uncertain

        # Draw box
        cv2.rectangle(canvas, (x, y), (x + w, y + h), color, 2)

        # Label background
        label_text = f"{emotion.capitalize()} ({int(confidence * 100)}%) - {status}"
        (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)

        # Ensure label fits within top image boundary
        label_y1 = max(0, y - th - 8)
        label_y2 = max(th + 8, y)
        cv2.rectangle(canvas, (x, label_y1), (x + tw + 10, label_y2), color, -1)

        # Draw white text
        cv2.putText(
            canvas,
            label_text,
            (x + 5, label_y2 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

    return canvas


def image_to_base64(img_bgr: np.ndarray, format: str = "JPEG") -> str:
    """Convert OpenCV BGR image matrix to base64 data URI string."""
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    buffer = io.BytesIO()
    pil_img.save(buffer, format=format)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    mime = "image/jpeg" if format.upper() == "JPEG" else "image/png"
    return f"data:{mime};base64,{encoded}"


def process_image(img_bgr: np.ndarray, file_name: str = "uploaded_image.jpg") -> dict:
    """
    Process a single still image through the full adapter pipeline.
    """
    cfg = load_config()
    data_source_label = "demo" if cfg.get("demo_mode", True) else "live"

    # Step 1: Preprocess (Module 1)
    processed_img = adapter_preprocess.preprocess(img_bgr, cfg)

    # Step 2: Detect faces (Module 2)
    boxes = adapter_face.detect_faces(processed_img, cfg)

    records = []
    if not boxes:
        # If no face detected, generate placeholder record
        rec = {
            "face_index": 0,
            "box": (0, 0, 0, 0),
            "scores": {emo: 0.0 for emo in adapter_emotion.EMOTION_CLASSES},
            "emotion": "None",
            "confidence": 0.0,
            "status": "Uncertain",
            "face_found": False
        }
        records.append(rec)
    else:
        for idx, box in enumerate(boxes):
            rec = adapter_emotion.predict_frame(processed_img, box, cfg, face_idx=idx)
            records.append(rec)

            # Append to results.csv
            storage.append_record(
                source="image",
                file_name=file_name,
                frame_number=0,
                face_id=idx,
                emotion=rec["emotion"],
                confidence=rec["confidence"],
                status=rec["status"],
                data_source=data_source_label
            )

    # Annotate image
    annotated_bgr = draw_detection_overlay(img_bgr, records)
    annotated_b64 = image_to_base64(annotated_bgr)

    return {
        "success": True,
        "file_name": file_name,
        "faces_detected": len(boxes),
        "records": records,
        "annotated_image": annotated_b64,
        "warnings": get_active_warnings()
    }


def process_webcam_frame(img_bgr: np.ndarray, frame_number: int = 0) -> dict:
    """
    Process an individual live webcam frame from the browser.
    """
    cfg = load_config()
    data_source_label = "demo" if cfg.get("demo_mode", True) else "live"

    processed = adapter_preprocess.preprocess(img_bgr, cfg)
    boxes = adapter_face.detect_faces(processed, cfg)

    records = []
    if boxes:
        for idx, box in enumerate(boxes):
            rec = adapter_emotion.predict_frame(processed, box, cfg, face_idx=idx)
            records.append(rec)

            storage.append_record(
                source="webcam",
                file_name="live_webcam",
                frame_number=frame_number,
                face_id=idx,
                emotion=rec["emotion"],
                confidence=rec["confidence"],
                status=rec["status"],
                data_source=data_source_label
            )

    annotated_bgr = draw_detection_overlay(img_bgr, records)
    annotated_b64 = image_to_base64(annotated_bgr)

    return {
        "success": True,
        "faces_detected": len(boxes),
        "records": records,
        "annotated_image": annotated_b64,
        "warnings": get_active_warnings()
    }
