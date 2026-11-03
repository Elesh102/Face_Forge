"""
=============================================================================
FaceForge - Module 4: Pipeline Controller (controller.py)
Contributed by: Member 4 (System Integration, UI, Storage & Analytics)
Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur

Responsibilities of Member 4:
- Central pipeline controller coordinating M1 (Preprocess), M2 (Face Detection),
  and M3 (Emotion Classification)
- Image annotation with bounding boxes, confidence badges, and labels
- Configuration management (config.yaml) with input sanitization and safety clamping
- Live webcam frame processing and temporal video frame sampling
=============================================================================
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
    """
    Updates config.yaml with sanitized values.
    Enforces strict type checks and value clamping to prevent application stalls.
    """
    current = load_config()

    # Validated sanitization
    if "demo_mode" in new_config:
        current["demo_mode"] = bool(new_config["demo_mode"])
    if "use_module1" in new_config:
        current["use_module1"] = bool(new_config["use_module1"])
    if "use_module2" in new_config:
        current["use_module2"] = bool(new_config["use_module2"])
    if "use_module3" in new_config:
        current["use_module3"] = bool(new_config["use_module3"])

    if "confidence_threshold" in new_config:
        try:
            val = float(new_config["confidence_threshold"])
            # Clamp between 0.05 (5%) and 0.99 (99%)
            current["confidence_threshold"] = round(max(0.05, min(0.99, val)), 2)
        except (ValueError, TypeError):
            pass

    if "video_sampling_step" in new_config:
        try:
            step = int(new_config["video_sampling_step"])
            # Clamp between 1 frame and 120 frames
            current["video_sampling_step"] = max(1, min(120, step))
        except (ValueError, TypeError):
            pass

    if "camera_index" in new_config:
        try:
            c_idx = int(new_config["camera_index"])
            current["camera_index"] = max(0, min(10, c_idx))
        except (ValueError, TypeError):
            pass

    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(current, f, default_flow_style=False)
    except Exception as e:
        print(f"[Error] Failed to write config.yaml: {e}")
    return current

def get_active_mode_badge() -> Dict[str, str]:
    """Returns the mode badge label and style based on active modules."""
    cfg = load_config()
    active_mods = []
    if cfg.get("use_module1", False):
        active_mods.append("M1: Preprocessing")
    if cfg.get("use_module2", False):
        active_mods.append("M2: Face Detection")
    if cfg.get("use_module3", False):
        active_mods.append("M3: Emotion Model")

    if active_mods:
        return {
            "text": f"Live: {', '.join(active_mods)}",
            "type": "live",
            "desc": f"Running with live teammate modules: {', '.join(active_mods)}."
        }
    if not cfg.get("demo_mode", True):
        return {
            "text": "Live module",
            "type": "live",
            "desc": "Operating with live plugged-in detection & classification modules."
        }
    return {
        "text": "Demo data",
        "type": "demo",
        "desc": "Operating with simulated mock adapters. Teammate modules pending."
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
    use_m1 = bool(cfg.get("use_module1", True))
    use_m2 = bool(cfg.get("use_module2", True))
    use_m3 = bool(cfg.get("use_module3", True))
    data_source = "demo" if cfg.get("demo_mode", False) else "live"
    threshold = float(cfg.get("confidence_threshold", 0.50))

    img = decode_image_bytes(image_bytes)
    if img is None:
        raise ValueError("Invalid image file format or corrupted bytes.")

    # Step 1: Preprocess
    preprocessed_img = adapter_preprocess.preprocess(img, use_real=use_m1)

    # Step 2: Detect faces
    boxes = adapter_face.detect_faces(preprocessed_img, use_real=use_m2)
    if not boxes:
        # Return clean result indicating 0 faces detected without fake box fabrication
        annotated_b64 = encode_image_base64(preprocessed_img)
        return {
            "status": "success",
            "file_name": file_name,
            "data_source": data_source,
            "badge": get_active_mode_badge(),
            "total_faces": 0,
            "records": [],
            "annotated_image_base64": f"data:image/jpeg;base64,{annotated_b64}"
        }

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
    use_m1 = bool(cfg.get("use_module1", True))
    use_m2 = bool(cfg.get("use_module2", True))
    use_m3 = bool(cfg.get("use_module3", True))
    data_source = "demo" if cfg.get("demo_mode", False) else "live"
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
    use_m1 = bool(cfg.get("use_module1", True))
    use_m2 = bool(cfg.get("use_module2", True))
    use_m3 = bool(cfg.get("use_module3", True))
    data_source = "demo" if cfg.get("demo_mode", False) else "live"
    threshold = float(cfg.get("confidence_threshold", 0.50))
    step = sampling_step or int(cfg.get("video_sampling_step", 10))

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        cap.release()
        raise ValueError("Could not open video file. Format may be unsupported or file is corrupted.")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    if total_frames <= 0 or fps <= 0:
        cap.release()
        raise ValueError("Video file contains 0 decodable frames.")

    duration_sec = round(total_frames / fps, 1)
    cap.release()

    # Dynamic step adjustment: ensure max ~80 frames to prevent multi-minute blocking
    if total_frames // step > 80:
        step = max(step, total_frames // 80)

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
