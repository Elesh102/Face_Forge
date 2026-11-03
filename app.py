"""
=============================================================================
FaceForge - Module 4: Main Application & API Gateway (app.py)
Contributed by: Member 4 (System Integration, UI, Storage & Analytics)
Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur

Responsibilities of Member 4:
- System Integration: Orchestrating Module 1, Module 2, and Module 3
- FastAPI backend REST endpoints for Image, Video, and Webcam inference
- Single-command launch serving both API and compiled React frontend
- Telemetry storage in CSV, data filtering, and analytics calculations
- Security PIN protection, CORS whitelist, and input validation
=============================================================================
"""

import os
import io
import asyncio
import shutil
import tempfile
import base64
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

import controller
import storage
import analytics

app = FastAPI(
    title="Face Forge API - Module 4",
    description="Backend API and pipeline orchestrator for Face Forge Emotion Detection System.",
    version="1.0.0"
)

# Secure CORS: Whitelist local frontend origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Ensure storage directory is initialized on startup
storage.init_storage()

@app.get("/api/health")
def read_root():
    """Health check endpoint for the FaceForge backend."""
    badge = controller.get_active_mode_badge()
    cfg = controller.load_config()
    return {
        "project": "Face Forge - Facial Emotion Recognition System",
        "group": "Group G2 (IT) - B.Tech Final Year Project",
        "institution": "SKIT Jaipur",
        "module": "Module 4: Integration, UI & Storage",
        "status": "online",
        "badge": badge,
        "config": cfg,
        "docs_url": "/docs"
    }

@app.get("/api/config")
def get_config():
    """Returns the current configuration and feature flags."""
    return controller.load_config()

@app.post("/api/config")
def update_config(payload: Dict[str, Any]):
    """
    Updates config.yaml with new feature flags and thresholds.
    FR-F1, FR-F2: Switches for Module 1, 2, 3, demo_mode, confidence threshold, video sampling step.
    """
    try:
        updated = controller.save_config(payload)
        return {"status": "success", "config": updated, "badge": controller.get_active_mode_badge()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")

@app.get("/api/status")
def get_status():
    """Returns active mode badge and module statuses without locking hardware devices."""
    cfg = controller.load_config()
    badge = controller.get_active_mode_badge()

    return {
        "badge": badge,
        "demo_mode": cfg.get("demo_mode", True),
        "modules": {
            "module1_preprocess": {
                "name": "Module 1: Preprocessing",
                "enabled": cfg.get("use_module1", False),
                "status": "Active (Demo Mock)" if not cfg.get("use_module1", False) else "Live (CLAHE & Normalization)"
            },
            "module2_face": {
                "name": "Module 2: Face Detection",
                "enabled": cfg.get("use_module2", False),
                "status": "Active (Demo Mock)" if not cfg.get("use_module2", False) else "Live (Haar Frontal + Profile Cascade)"
            },
            "module3_emotion": {
                "name": "Module 3: Emotion Model",
                "enabled": cfg.get("use_module3", False),
                "status": "Active (Demo Mock)" if not cfg.get("use_module3", False) else "Live (ONNX FERPlus Deep CNN)"
            }
        },
        "camera_index_0_found": True
    }

@app.post("/api/detect/image")
async def detect_image(
    file: UploadFile = File(...)
):
    """
    FR-B1 to FR-B5: Upload JPG/PNG image, run pipeline, return Result Records and annotated image.
    """
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
        result = controller.process_single_image(
            image_bytes=contents,
            file_name=file.filename or "uploaded_image.jpg",
            source="image"
        )
        return result
    except Exception as e:
        # NFR-2: Never crash on bad input
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": f"Image processing failed: {str(e)}"}
        )

@app.post("/api/detect/video")
async def detect_video(
    file: UploadFile = File(...),
    sampling_step: Optional[int] = Form(None)
):
    """
    FR-C1 to FR-C6: Upload MP4/AVI video, sample frames, return frame count, duration, and predictions.
    Offloaded to thread pool to prevent blocking concurrent HTTP requests.
    """
    temp_path = None
    try:
        contents = await file.read()
        if not contents or len(contents) < 64:
            raise HTTPException(status_code=400, detail="Uploaded video file is empty or corrupted.")
        
        # Save temporary file for OpenCV VideoCapture
        suffix = os.path.splitext(file.filename or "")[1] or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contents)
            temp_path = tmp.name

        # Offload CPU-heavy video processing to background worker thread
        result = await asyncio.to_thread(
            controller.process_video_file,
            video_path=temp_path,
            file_name=file.filename or "uploaded_video.mp4",
            sampling_step=sampling_step
        )
        return result
    except ValueError as ve:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(ve)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": f"Video processing error: {str(e)}"}
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

@app.post("/api/detect/webcam-frame")
async def detect_webcam_frame(
    file: Optional[UploadFile] = File(None),
    base64_data: Optional[str] = Form(None),
    save_result: Optional[bool] = Form(False)
):
    """
    FR-D1 to FR-D3: Processes a live frame captured from browser webcam or camera.
    """
    try:
        frame_bytes = None
        if file is not None:
            frame_bytes = await file.read()
        elif base64_data:
            # Strip data URL prefix if present
            if "," in base64_data:
                base64_data = base64_data.split(",", 1)[1]
            frame_bytes = base64.b64decode(base64_data)
        
        if not frame_bytes:
            raise HTTPException(status_code=400, detail="No frame data provided.")

        result = controller.process_webcam_frame(
            frame_bytes=frame_bytes,
            save_to_storage=bool(save_result)
        )
        return result
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": f"Webcam frame error: {str(e)}"}
        )

@app.get("/api/results")
def get_results_table(
    source: Optional[str] = Query(None),
    emotion: Optional[str] = Query(None),
    data_source: Optional[str] = Query(None)
):
    """
    FR-E2: Results page table data with filters for source, emotion, and data_source.
    """
    df = storage.load_results()
    if df.empty:
        return {"total": 0, "rows": []}

    filtered = df.copy()
    if source and source.lower() != "all":
        filtered = filtered[filtered["source"].str.lower() == source.lower()]
    if emotion and emotion.lower() != "all":
        filtered = filtered[filtered["emotion"].str.lower() == emotion.lower()]
    if data_source and data_source.lower() != "all":
        filtered = filtered[filtered["data_source"].str.lower() == data_source.lower()]

    # Sort most recent first
    rows = filtered.to_dict(orient="records")
    rows.reverse()
    return {"total": len(rows), "rows": rows}

@app.get("/api/results/download")
def download_results():
    """FR-E3: Download results as CSV."""
    storage.init_storage()
    if not os.path.exists(storage.RESULTS_CSV):
        raise HTTPException(status_code=404, detail="Results CSV file not found.")
    return FileResponse(
        storage.RESULTS_CSV,
        media_type="text/csv",
        filename="face_forge_results.csv"
    )

@app.get("/api/download/dataset-pdf")
def download_dataset_pdf():
    """Serves the generated FER-2013 Dataset Specification & Training Report PDF."""
    pdf_path = os.path.join(os.path.dirname(__file__), "FaceForge_FER2013_Dataset_Specification_Report.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Dataset specification PDF not found.")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="FaceForge_FER2013_Dataset_Specification_Report.pdf"
    )

@app.get("/api/download/guide-pdf")
def download_guide_pdf():
    """Serves the generated Teammate Integration Guide PDF."""
    pdf_path = os.path.join(os.path.dirname(__file__), "FaceForge_Teammate_Integration_Guide.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Integration guide PDF not found.")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="FaceForge_Teammate_Integration_Guide.pdf"
    )

@app.delete("/api/results/clear")
def clear_results_endpoint(
    pin: Optional[str] = Query(None, description="Admin security PIN required to clear records")
):
    """
    FR-E7: Clear results file with admin PIN authentication protection.
    Prevents unauthorized deletion of telemetry records.
    """
    if pin != "1234":
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Admin PIN '1234' is required to clear telemetry records."
        )

    success = storage.clear_results()
    if success:
        return {"status": "success", "message": "All result records cleared successfully."}
    raise HTTPException(status_code=500, detail="Failed to clear results file.")

@app.get("/api/analytics")
def get_analytics(
    data_source: str = Query("all", description="all, demo, or live")
):
    """
    FR-E4 to FR-E6: Analytics data (emotion distribution, timeline, most frequent, avg confidence).
    """
    df = storage.load_results()
    stats = analytics.compute_analytics(df, data_source_filter=data_source)
    return stats

@app.get("/api/evaluation")
def get_evaluation():
    """
    FR-F6: Module 3 evaluation page showing metrics_report.txt and confusion_matrix.png if present.
    """
    report_path = os.path.join(storage.RESULTS_DIR, "metrics_report.txt")
    cm_path = os.path.join(storage.RESULTS_DIR, "confusion_matrix.png")

    report_text = None
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_text = f.read()
        except Exception:
            report_text = "Error reading metrics_report.txt"

    cm_base64 = None
    if os.path.exists(cm_path):
        try:
            with open(cm_path, "rb") as f:
                cm_base64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        except Exception:
            cm_base64 = None

    return {
        "report_available": report_text is not None,
        "metrics_report": report_text,
        "confusion_matrix_available": cm_base64 is not None,
        "confusion_matrix_image": cm_base64
    }

# Mount React frontend static build if available (FR-A1: Single Command Launch)
dist_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(dist_dir):
    from starlette.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")

if __name__ == "__main__":
    # Single command launch for FaceForge
    print("[Face Forge] Starting server on http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
