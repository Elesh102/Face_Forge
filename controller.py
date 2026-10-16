"""
Face Forge - Module 4 Controller (controller.py)
Orchestrates the detection pipeline across adapters, configuration, and storage.
"""

from typing import Dict, Any, List, Tuple, Optional
import os
import io
import base64
import yaml
import cv2
import numpy as np

import adapter_preprocess
import adapter_face
import adapter_emotion
import storage

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

DEFAULT_CONFIG = {
    "demo_mode": True,
    "use_module1": False,
    "use_module2": False,
    "use_module3": False,
    "confidence_threshold": 0.50,
    "video_sampling_step": 10
}

def load_config() -> Dict[str, Any]:
    """Reads config.yaml safely, creating default if missing."""
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            if not isinstance(cfg, dict):
                return DEFAULT_CONFIG.copy()
            # Merge with defaults
            merged = DEFAULT_CONFIG.copy()
            merged.update(cfg)
            return merged
    except Exception as e:
        print(f"[Warning] Failed to load config.yaml: {e}. Using defaults.")
        return DEFAULT_CONFIG.copy()

def save_config(new_config: Dict[str, Any]) -> Dict[str, Any]:
    """Updates config.yaml with new values."""
    current = load_config()
    current.update(new_config)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(current, f, default_flow_style=False)
    except Exception as e:
        print(f"[Error] Failed to write config.yaml: {e}")
    return current

def get_active_mode_badge() -> Dict[str, str]:
    """Returns the honesty badge label and style based on demo_mode flag."""
    cfg = load_config()
    if cfg.get("demo_mode", True):
        return {
            "text": "Demo data",
            "type": "demo",
            "desc": "Operating with simulated mock adapters. Teammate modules pending."
        }
    return {
        "text": "Live module",
        "type": "live",
        "desc": "Operating with live plugged-in detection & classification modules."
    }

def annotate_image(img: np.ndarray, records: List[Dict[str, Any]]) -> np.ndarray:
    """
    Draws professional bounding boxes and detected expression labels on image.
    """
    annotated = img.copy()
    h, w = annotated.shape[:2]

    # Emotion color map (BGR format)
    color_map = {
        "happy": (46, 204, 113),      # Emerald
        "neutral": (160, 160, 160),    # Slate grey
        "surprise": (241, 196, 15),   # Yellow/gold
        "sad": (230, 126, 34),        # Amber
        "angry": (41, 128, 185),      # Fiery Crimson (BGR)
        "fear": (155, 89, 182),       # Amethyst
        "disgust": (52, 73, 94)       # Charcoal
    }

    for rec in records:
        box = rec.get("box", [0, 0, 0, 0])
        x, y, bw, bh = box
        emotion = rec.get("emotion", "neutral").lower()
        confidence = rec.get("confidence", 0.0)
        status = rec.get("status", "Neutral")

        box_color = color_map.get(emotion, (6, 182, 212))

        # Draw smooth rounded-corner rectangle effect
        cv2.rectangle(annotated, (x, y), (x + bw, y + bh), box_color, 2, cv2.LINE_AA)

        # Label background pill
        label = f"{emotion.capitalize()} ({int(confidence * 100)}%) - {status}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.45, min(0.65, bw / 300.0))
        thickness = 1
        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)

        label_y = max(y - 8, text_h + 10)
        cv2.rectangle(
            annotated,
            (x, label_y - text_h - 6),
            (x + text_w + 12, label_y + baseline + 2),
            box_color,
            -1
        )
        cv2.putText(
            annotated,
            label,
            (x + 6, label_y - 2),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA
        )

    return annotated

def encode_image_base64(img: np.ndarray) -> str:
    """Encodes BGR cv2 image to base64 JPEG string."""
    success, buffer = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not success:
        return ""
    return base64.b64encode(buffer).decode("utf-8")

def decode_image_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    """Decodes raw image bytes into BGR cv2 array."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def process_single_image(
    image_bytes: bytes,
    file_name: str = "upload.jpg",
    source: str = "image"
) -> Dict[str, Any]:
    """
    Executes the full Module 4 pipeline on a still image:
    1. Preprocess (Module 1 adapter)
    2. Face detection (Module 2 adapter)
    3. Emotion classification (Module 3 adapter)
    4. Result record generation & persistence (storage.py)
    5. Annotated visual generation
    """
    cfg = load_config()
    data_source = "demo" if cfg.get("demo_mode", True) else "live"
    use_m1 = cfg.get("use_module1", False) and not cfg.get("demo_mode", True)
    use_m2 = cfg.get("use_module2", False) and not cfg.get("demo_mode", True)
    use_m3 = cfg.get("use_module3", False) and not cfg.get("demo_mode", True)
    threshold = float(cfg.get("confidence_threshold", 0.50))

    img = decode_image_bytes(image_bytes)
    if img is None:
        raise ValueError("Invalid image file format or corrupted bytes.")

    # Step 1: Preprocess
    preprocessed_img = adapter_preprocess.preprocess(img, use_real=use_m1)

    # Step 2: Detect faces
    boxes = adapter_face.detect_faces(preprocessed_img, use_real=use_m2)
    if not boxes:
        # Fallback centered box if none found
        h, w = preprocessed_img.shape[:2]
        boxes = [(int(w * 0.25), int(h * 0.2), int(w * 0.5), int(h * 0.5))]

    records = []
    for face_idx, box in enumerate(boxes):
        crop = adapter_face.crop_face(preprocessed_img, box)
        record = adapter_emotion.predict_face(
            face_img=crop,
            box=box,
            face_index=face_idx,
            confidence_threshold=threshold,
            use_real=use_m3
        )
        records.append(record)

        # Step 4: Persist to CSV
        storage.save_result(
            source=source,
            file_name=file_name,
            frame_number=0,
            face_id=face_idx,
            emotion=record["emotion"],
            confidence=record["confidence"],
            status=record["status"],
            data_source=data_source
        )

    # Step 5: Visual annotations
    annotated = annotate_image(preprocessed_img, records)
    annotated_b64 = encode_image_base64(annotated)

    return {
        "status": "success",
        "file_name": file_name,
        "data_source": data_source,
        "badge": get_active_mode_badge(),
        "total_faces": len(records),
        "records": records,
        "annotated_image_base64": f"data:image/jpeg;base64,{annotated_b64}"
    }

def process_webcam_frame(
    frame_bytes: bytes,
    save_to_storage: bool = False
) -> Dict[str, Any]:
    """
    Processes a live webcam frame in real time.
    """
    cfg = load_config()
    data_source = "demo" if cfg.get("demo_mode", True) else "live"
    use_m1 = cfg.get("use_module1", False) and not cfg.get("demo_mode", True)
    use_m2 = cfg.get("use_module2", False) and not cfg.get("demo_mode", True)
    use_m3 = cfg.get("use_module3", False) and not cfg.get("demo_mode", True)
    threshold = float(cfg.get("confidence_threshold", 0.50))

    img = decode_image_bytes(frame_bytes)
    if img is None:
        raise ValueError("Could not decode webcam frame.")

    preprocessed = adapter_preprocess.preprocess(img, use_real=use_m1)
    boxes = adapter_face.detect_faces(preprocessed, use_real=use_m2)

    records = []
    for idx, box in enumerate(boxes):
        crop = adapter_face.crop_face(preprocessed, box)
        rec = adapter_emotion.predict_face(
            face_img=crop,
            box=box,
            face_index=idx,
            confidence_threshold=threshold,
            use_real=use_m3
        )
        records.append(rec)

        if save_to_storage:
            storage.save_result(
                source="webcam",
                file_name="webcam_live",
                frame_number=0,
                face_id=idx,
                emotion=rec["emotion"],
                confidence=rec["confidence"],
                status=rec["status"],
                data_source=data_source
            )

    annotated = annotate_image(preprocessed, records)
    annotated_b64 = encode_image_base64(annotated)

    return {
        "records": records,
        "data_source": data_source,
        "annotated_frame_base64": f"data:image/jpeg;base64,{annotated_b64}"
    }

def process_video_file(
    video_path: str,
    file_name: str = "video.mp4",
    sampling_step: Optional[int] = None
) -> Dict[str, Any]:
    """
    Processes video frames sampled at regular intervals.
    """
    cfg = load_config()
    data_source = "demo" if cfg.get("demo_mode", True) else "live"
    use_m1 = cfg.get("use_module1", False) and not cfg.get("demo_mode", True)
    use_m2 = cfg.get("use_module2", False) and not cfg.get("demo_mode", True)
    use_m3 = cfg.get("use_module3", False) and not cfg.get("demo_mode", True)
    threshold = float(cfg.get("confidence_threshold", 0.50))
    step = sampling_step or int(cfg.get("video_sampling_step", 10))

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    duration_sec = round(total_frames / fps, 1) if fps > 0 else 0
    cap.release()

    sampled_records = []
    preview_frames = []
    frame_count = 0

    for frame_idx, frame in adapter_face.read_video(video_path, step=step):
        frame_count += 1
        preprocessed = adapter_preprocess.preprocess(frame, use_real=use_m1)
        boxes = adapter_face.detect_faces(preprocessed, use_real=use_m2)

        for f_idx, box in enumerate(boxes):
            crop = adapter_face.crop_face(preprocessed, box)
            rec = adapter_emotion.predict_face(
                face_img=crop,
                box=box,
                face_index=f_idx,
                confidence_threshold=threshold,
                use_real=use_m3
            )
            rec["frame_number"] = frame_idx
            rec["time_sec"] = round(frame_idx / fps, 2)
            sampled_records.append(rec)

            storage.save_result(
                source="video",
                file_name=file_name,
                frame_number=frame_idx,
                face_id=f_idx,
                emotion=rec["emotion"],
                confidence=rec["confidence"],
                status=rec["status"],
                data_source=data_source
            )

        # Store a couple of preview snapshots
        if len(preview_frames) < 4:
            annotated = annotate_image(preprocessed, sampled_records[-len(boxes):])
            b64 = encode_image_base64(annotated)
            preview_frames.append({
                "frame_number": frame_idx,
                "time_sec": round(frame_idx / fps, 2),
                "image": f"data:image/jpeg;base64,{b64}"
            })

    return {
        "status": "success",
        "file_name": file_name,
        "total_video_frames": total_frames,
        "duration_sec": duration_sec,
        "sampled_frames_processed": frame_count,
        "sampling_step": step,
        "data_source": data_source,
        "badge": get_active_mode_badge(),
        "records": sampled_records,
        "preview_frames": preview_frames
    }
