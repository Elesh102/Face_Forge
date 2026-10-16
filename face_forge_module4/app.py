"""
app.py — Face Forge Module 4 Main Flask Application
===================================================

Entry point for the web server. Provides routing for all pages:
  - Home (/)
  - Image Detection (/image)
  - Video Detection (/video)
  - Webcam Detection (/webcam)
  - Results (/results)
  - Analytics (/analytics)
  - Module Hub (/module_hub)
  - Settings (/settings)
  - About (/about)
"""

import os
import io
import base64
import tempfile
import cv2
import numpy as np
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    jsonify,
    Response
)

import controller
import storage
import analytics

app = Flask(__name__)
app.secret_key = "face_forge_module4_secret_key_2026"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB max upload

# Initialize results directory and CSV on boot
storage.init_storage()


@app.context_processor
def inject_global_data():
    """Inject mode badge and warnings into all templates."""
    badge = controller.get_badge_info()
    warnings = controller.get_active_warnings()
    cfg = controller.load_config()
    return dict(badge=badge, warnings=warnings, config=cfg)


# =========================================================================
# 1. Home Page
# =========================================================================
@app.route("/")
def home():
    return render_template("home.html", active_page="home")


# =========================================================================
# 2. Image Detection Page
# =========================================================================
@app.route("/image", methods=["GET", "POST"])
def image_detection():
    result = None
    if request.method == "POST":
        file = request.files.get("image_file")
        if not file or file.filename == "":
            flash("Please choose an image file (JPG or PNG).", "warning")
            return redirect(url_for("image_detection"))

        try:
            file_bytes = np.frombuffer(file.read(), np.uint8)
            img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if img_bgr is None:
                flash("Could not decode image. Please upload a valid JPG or PNG.", "error")
                return redirect(url_for("image_detection"))

            result = controller.process_image(img_bgr, file_name=file.filename)
            flash("Image processed successfully through the pipeline.", "success")
        except Exception as e:
            flash(f"Error processing image: {str(e)}", "error")

    return render_template("image.html", active_page="image", result=result)


# =========================================================================
# 3. Video Detection Page
# =========================================================================
@app.route("/video", methods=["GET", "POST"])
def video_detection():
    result = None
    if request.method == "POST":
        file = request.files.get("video_file")
        step_val = request.form.get("sampling_step", None)

        if not file or file.filename == "":
            flash("Please choose a video file (MP4 or AVI).", "warning")
            return redirect(url_for("video_detection"))

        # Parse sampling step
        cfg = controller.load_config()
        try:
            step = int(step_val) if step_val else int(cfg.get("video_sampling_step", 10))
            step = max(1, step)
        except ValueError:
            step = 10

        # Save to temporary file for OpenCV reading
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"upload_{file.filename}")
        file.save(temp_path)

        try:
            from adapters.adapter_face import read_video, get_video_total_frames
            from adapters import adapter_preprocess, adapter_emotion

            total_frames = get_video_total_frames(temp_path)
            processed_records = []
            sampled_frames_count = 0
            data_source_label = "demo" if cfg.get("demo_mode", True) else "live"

            for frame_idx, frame in read_video(temp_path, step=step):
                sampled_frames_count += 1
                processed_frame = adapter_preprocess.preprocess(frame, cfg)
                boxes = adapter_face.detect_faces(processed_frame, cfg)

                for face_idx, box in enumerate(boxes):
                    rec = adapter_emotion.predict_frame(processed_frame, box, cfg, face_idx=face_idx)
                    rec["frame_number"] = frame_idx
                    processed_records.append(rec)

                    # Save to storage
                    storage.append_record(
                        source="video",
                        file_name=file.filename,
                        frame_number=frame_idx,
                        face_id=face_idx,
                        emotion=rec["emotion"],
                        confidence=rec["confidence"],
                        status=rec["status"],
                        data_source=data_source_label
                    )

            result = {
                "file_name": file.filename,
                "total_frames": total_frames,
                "sampled_frames": sampled_frames_count,
                "step": step,
                "records": processed_records
            }
            flash(f"Video analysis complete: sampled {sampled_frames_count} frames out of {total_frames}.", "success")
        except Exception as e:
            flash(f"Error analyzing video: {str(e)}", "error")
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    return render_template("video.html", active_page="video", result=result)


# =========================================================================
# 4. Webcam Detection Page
# =========================================================================
@app.route("/webcam")
def webcam_detection():
    return render_template("webcam.html", active_page="webcam")


@app.route("/api/webcam/predict", methods=["POST"])
def api_webcam_predict():
    """AJAX endpoint that receives a base64 camera frame and returns detection overlay."""
    try:
        data = request.get_json(force=True)
        image_data = data.get("image", "")
        frame_num = int(data.get("frame_number", 0))

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img_bgr is None:
            return jsonify({"success": False, "error": "Invalid frame data"}), 400

        result = controller.process_webcam_frame(img_bgr, frame_number=frame_num)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =========================================================================
# 5. Results Page
# =========================================================================
@app.route("/results")
def results_view():
    source = request.args.get("source", "all")
    emotion = request.args.get("emotion", "all")
    date_val = request.args.get("date", "")
    data_source = request.args.get("data_source", "all")

    rows = storage.filter_records(
        source=source,
        emotion=emotion,
        date_filter=date_val,
        data_source=data_source
    )

    return render_template(
        "results.html",
        active_page="results",
        records=rows,
        total_count=len(rows),
        filter_source=source,
        filter_emotion=emotion,
        filter_date=date_val,
        filter_data_source=data_source
    )


@app.route("/results/download")
def download_results():
    """Download results.csv file."""
    if not os.path.exists(storage.CSV_PATH):
        storage.init_storage()

    return send_file(
        storage.CSV_PATH,
        mimetype="text/csv",
        as_attachment=True,
        download_name="face_forge_results.csv"
    )


@app.route("/results/clear", methods=["POST"])
def clear_results():
    """Clear all records from results.csv."""
    if storage.clear_results():
        flash("Results ledger cleared successfully.", "success")
    else:
        flash("Failed to clear results ledger.", "error")
    return redirect(url_for("results_view"))


# =========================================================================
# 6. Analytics Page
# =========================================================================
@app.route("/analytics")
def analytics_view():
    data_tier = request.args.get("tier", "all")
    stats = analytics.get_analytics(data_source=data_tier)
    return render_template(
        "analytics.html",
        active_page="analytics",
        stats=stats,
        selected_tier=data_tier
    )


# =========================================================================
# 7. Module Hub (IMPORTANT)
# =========================================================================
@app.route("/module_hub", methods=["GET", "POST"])
def module_hub():
    cfg = controller.load_config()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "toggle_module1":
            cfg["use_module1"] = not cfg.get("use_module1", False)
        elif action == "toggle_module2":
            cfg["use_module2"] = not cfg.get("use_module2", False)
        elif action == "toggle_module3":
            cfg["use_module3"] = not cfg.get("use_module3", False)

        controller.save_config(cfg)
        flash("Module configuration updated.", "success")
        return redirect(url_for("module_hub"))

    # Check Module 3 evaluation files in results/
    metrics_path = os.path.join(storage.RESULTS_DIR, "metrics_report.txt")
    cm_path = os.path.join(storage.RESULTS_DIR, "confusion_matrix.png")

    metrics_text = None
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics_text = f.read()
        except Exception:
            metrics_text = "Error reading metrics_report.txt"

    cm_image_b64 = None
    if os.path.exists(cm_path):
        try:
            with open(cm_path, "rb") as f:
                cm_image_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        except Exception:
            cm_image_b64 = None

    return render_template(
        "module_hub.html",
        active_page="module_hub",
        config=cfg,
        metrics_text=metrics_text,
        confusion_matrix_b64=cm_image_b64
    )


# =========================================================================
# 8. Settings Page
# =========================================================================
@app.route("/settings", methods=["GET", "POST"])
def settings_view():
    cfg = controller.load_config()

    if request.method == "POST":
        try:
            cfg["demo_mode"] = "demo_mode" in request.form
            cfg["use_module1"] = "use_module1" in request.form
            cfg["use_module2"] = "use_module2" in request.form
            cfg["use_module3"] = "use_module3" in request.form
            cfg["confidence_threshold"] = float(request.form.get("confidence_threshold", 0.50))
            cfg["video_sampling_step"] = int(request.form.get("video_sampling_step", 10))

            if controller.save_config(cfg):
                flash("Settings saved successfully.", "success")
            else:
                flash("Failed to save settings to config.yaml.", "error")
        except Exception as e:
            flash(f"Error parsing settings: {str(e)}", "error")

        return redirect(url_for("settings_view"))

    return render_template("settings.html", active_page="settings", config=cfg)


# =========================================================================
# 9. About Page
# =========================================================================
@app.route("/about")
def about_view():
    return render_template("about.html", active_page="about")


# =========================================================================
# Error Handlers (Readable message, never crash)
# =========================================================================
@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", code=404, message="The requested page could not be found."), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", code=500, message="An internal system error occurred. Pipeline preserved."), 500


if __name__ == "__main__":
    print("[Face Forge Module 4] Starting server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
