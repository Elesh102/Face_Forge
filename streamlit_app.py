"""
Face Forge - Module 4 Streamlit Viva Companion (streamlit_app.py)
Provides the native Streamlit UI as requested in section 2.4 of the project SRS.
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import cv2
from PIL import Image

import controller
import storage
import analytics

st.set_page_config(
    page_title="Face Forge - Emotion Detection System",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #0b0f19; color: #f8fafc; }
    .badge-demo {
        background: linear-gradient(135deg, #d97706, #b45309);
        color: white; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem;
    }
    .badge-live {
        background: linear-gradient(135deg, #059669, #047857);
        color: white; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

cfg = controller.load_config()
is_demo = cfg.get("demo_mode", True)
badge_class = "badge-demo" if is_demo else "badge-live"
badge_text = "Demo data" if is_demo else "Live module"

# Sidebar Navigation
st.sidebar.title("🎭 Face Forge")
st.sidebar.markdown(f'<span class="{badge_class}">{badge_text}</span>', unsafe_allow_html=True)
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navigation", ["Home", "Image Mode", "Video Mode", "Webcam Mode", "Results", "Analytics", "Settings", "Evaluation"])

# ----------------- HOME -----------------
if menu == "Home":
    st.title("Face Forge")
    st.subheader("Facial Expression Analysis & Integration Platform (Module 4)")
    st.markdown("Select a detection mode below or use the sidebar to access stored results and analytics.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🖼️ **Image Mode**\n\nUpload still images (JPG/PNG) to detect facial expressions and bounding boxes.")
    with col2:
        st.info("🎬 **Video Mode**\n\nProcess video files (MP4/AVI) with configurable frame sampling intervals.")
    with col3:
        st.info("📹 **Webcam Mode**\n\nLive webcam feed with real-time expression detection placeholder.")

    st.markdown("---")
    st.caption("Ethical Note: This system identifies detected facial expressions, not a person's inner feeling.")

# ----------------- IMAGE MODE -----------------
elif menu == "Image Mode":
    st.title("Image Detection Mode")
    st.markdown(f'<span class="{badge_class}">{badge_text}</span>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        image = Image.open(uploaded_file)
        
        col_img, col_res = st.columns([1, 1])
        with col_img:
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
        if st.button("Start Detection", type="primary"):
            with st.spinner("Processing image through Module 1, 2, and 3 adapters..."):
                res = controller.process_single_image(file_bytes, file_name=uploaded_file.name, source="image")
                
                with col_res:
                    st.success(f"Detected {res['total_faces']} face(s)")
                    st.write("### Detected Expressions:")
                    for rec in res["records"]:
                        st.markdown(f"**Face #{rec['face_index']}**: `{rec['emotion'].upper()}` ({int(rec['confidence']*100)}%) | Status: **{rec['status']}**")
                        st.progress(float(rec['confidence']))

# ----------------- VIDEO MODE -----------------
elif menu == "Video Mode":
    st.title("Video Detection Mode")
    st.markdown(f'<span class="{badge_class}">{badge_text}</span>', unsafe_allow_html=True)
    
    video_file = st.file_uploader("Upload a Video", type=["mp4", "avi"])
    step = st.slider("Frame Sampling Interval (every Nth frame)", min_value=1, max_value=60, value=int(cfg.get("video_sampling_step", 10)))
    
    if video_file is not None:
        if st.button("Process Video", type="primary"):
            st.info("Processing video frames... This demonstrates the frame sampling pipeline.")
            # Save temporarily
            with open("temp_video.mp4", "wb") as f:
                f.write(video_file.read())
            res = controller.process_video_file("temp_video.mp4", file_name=video_file.name, sampling_step=step)
            st.success(f"Finished! Processed {res['sampled_frames_processed']} sampled frames.")
            st.dataframe(pd.DataFrame(res["records"]))

# ----------------- WEBCAM MODE -----------------
elif menu == "Webcam Mode":
    st.title("Webcam Mode")
    st.markdown(f'<span class="{badge_class}">{badge_text}</span>', unsafe_allow_html=True)
    
    st.warning("Webcam Placeholder - Waiting for Module 2/3 hardware integration.")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.button("Start Camera (Placeholder)", disabled=True)
    with col_w2:
        st.button("Stop Camera (Placeholder)", disabled=True)
    st.info("Note: The React Frontend provides interactive live browser webcam feed with real-time expression detection!")

# ----------------- RESULTS -----------------
elif menu == "Results":
    st.title("Detection Results History")
    df = storage.load_results()
    if df.empty:
        st.info("No detection records found in results/results.csv. Run an image or video detection first.")
    else:
        st.dataframe(df, use_container_width=True)
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv_data, file_name="results.csv", mime="text/csv")
        
        if st.button("Clear Results File"):
            storage.clear_results()
            st.success("Results cleared! Refresh to update.")

# ----------------- ANALYTICS -----------------
elif menu == "Analytics":
    st.title("Analytics & Insights")
    df = storage.load_results()
    stats = analytics.compute_analytics(df)
    
    if not stats["has_data"]:
        st.info("No data available to calculate analytics.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Records", stats["total_records"])
        m2.metric("Dominant Expression", stats["most_frequent_emotion"])
        m3.metric("Average Confidence", f"{int(stats['average_confidence'] * 100)}%")
        
        st.subheader("Emotion Distribution")
        dist_df = pd.DataFrame([
            {"Emotion": k.capitalize(), "Count": v["count"], "Percentage": f"{v['percentage']}%"}
            for k, v in stats["emotion_distribution"].items()
        ])
        st.table(dist_df)

# ----------------- SETTINGS -----------------
elif menu == "Settings":
    st.title("System Settings & Feature Flags")
    with st.form("settings_form"):
        demo_mode = st.checkbox("Demo Mode (Active now)", value=cfg.get("demo_mode", True))
        m1 = st.checkbox("Use Module 1 (Preprocessing)", value=cfg.get("use_module1", False))
        m2 = st.checkbox("Use Module 2 (Face Detection)", value=cfg.get("use_module2", False))
        m3 = st.checkbox("Use Module 3 (Emotion Model)", value=cfg.get("use_module3", False))
        thresh = st.slider("Confidence Threshold", 0.1, 1.0, float(cfg.get("confidence_threshold", 0.50)), 0.05)
        step = st.number_input("Video Sampling Step", min_value=1, max_value=100, value=int(cfg.get("video_sampling_step", 10)))
        
        if st.form_submit_button("Save Settings"):
            controller.save_config({
                "demo_mode": demo_mode,
                "use_module1": m1,
                "use_module2": m2,
                "use_module3": m3,
                "confidence_threshold": thresh,
                "video_sampling_step": step
            })
            st.success("Settings saved to config.yaml!")

# ----------------- EVALUATION -----------------
elif menu == "Evaluation":
    st.title("Module 3 Evaluation Report")
    report_path = os.path.join(storage.RESULTS_DIR, "metrics_report.txt")
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            st.code(f.read())
    else:
        st.info("Waiting for Module 3 evaluation files (metrics_report.txt).")
