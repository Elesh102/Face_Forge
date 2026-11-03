"""
create_srs_diagrams.py
======================
Generates all 11 high-resolution architectural and UML diagrams for the
FaceForge SRS document, matching Team B's diagram format exactly.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

OUTPUT_DIR = "srs_diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper to save figure cleanly
def save_fig(fig, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: {filepath}")

# =========================================================================
# Figure 1: Agile Development Model
# =========================================================================
def make_fig1():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.axis('off')

    # Draw circular segment badges
    colors_list = ['#e11d48', '#ea580c', '#f59e0b', '#0284c7', '#2563eb', '#059669']
    stages = ['Plan', 'Design', 'Develop', 'Test', 'Release', 'Feedback']
    angles = [90, 30, 330, 270, 210, 150]
    
    # Draw central circle
    center_circle = plt.Circle((0.5, 0.5), 0.22, color='white', ec='#0f172a', lw=2, zorder=10)
    ax.add_patch(center_circle)
    ax.text(0.5, 0.5, "AGILE", ha='center', va='center', fontsize=18, fontweight='bold', color='#0f172a', zorder=11)

    # Draw outer wedges
    for i, (stage, col) in enumerate(zip(stages, colors_list)):
        wedge = patches.Wedge((0.5, 0.5), 0.42, 60*i, 60*(i+1), width=0.18, facecolor=col, edgecolor='white', lw=2)
        ax.add_patch(wedge)
        # Text position
        import numpy as np
        rad = np.deg2rad(60*i + 30)
        tx = 0.5 + 0.32 * np.cos(rad)
        ty = 0.5 + 0.32 * np.sin(rad)
        ax.text(tx, ty, stage, ha='center', va='center', fontsize=9.5, fontweight='bold', color='white')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig1_agile.png")

# =========================================================================
# Figure 2: System Architecture Diagram
# =========================================================================
def make_fig2():
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.axis('off')

    def draw_box(x, y, w, h, title, items, bg='#ffffff', ec='#0f172a'):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", fc=bg, ec=ec, lw=1.2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.04, title, ha='center', va='top', fontsize=8.5, fontweight='bold', color='#0f172a')
        ax.plot([x, x+w], [y + h - 0.065, y + h - 0.065], color=ec, lw=0.8)
        curr_y = y + h - 0.10
        for it in items:
            ax.text(x + 0.02, curr_y, it, ha='left', va='top', fontsize=7.2, color='#334155')
            curr_y -= 0.035

    # Columns: Users, Client, App Server, Storage, ML Engine
    draw_box(0.02, 0.2, 0.16, 0.65, "USERS", ["Member 4 / User", "• Image Testing", "• Video Processing", "• Live Webcam", "• View Analytics", "• Manage Config"])
    draw_box(0.22, 0.2, 0.20, 0.65, "BROWSER / CLIENT", ["React 19 + Vite", "• HomeView", "• ImageView (Upload)", "• VideoView (Sampling)", "• WebcamView (Stream)", "• ResultsView (Ledger)", "• AnalyticsView (Charts)"])
    draw_box(0.46, 0.15, 0.24, 0.75, "APPLICATION SERVER", ["FastAPI Gateway (app.py)", "• /api/detect/image", "• /api/detect/video", "• /api/detect/webcam", "• /api/results & /clear", "• /api/analytics", "• /api/config", "• CORS & StaticFiles"])
    draw_box(0.74, 0.52, 0.24, 0.38, "STORAGE SERVICES", ["storage.py Ledger", "• results.csv (Append-only)", "• config.yaml", "• analytics.py Aggregator", "• pandas & matplotlib"])
    draw_box(0.74, 0.10, 0.24, 0.38, "AI & CV ADAPTERS", ["controller.py Dispatcher", "• Preprocess (M1 Stub)", "• Face Detection (M2 Stub)", "• Emotion Model (M3 Stub)", "• Pretrained FER Net"])

    # Connecting arrows
    ax.annotate('', xy=(0.22, 0.55), xytext=(0.18, 0.55), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.annotate('', xy=(0.46, 0.55), xytext=(0.42, 0.55), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.annotate('', xy=(0.74, 0.70), xytext=(0.70, 0.70), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))
    ax.annotate('', xy=(0.74, 0.30), xytext=(0.70, 0.30), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig2_system_architecture.png")

# =========================================================================
# Figure 3: DFD Level 0 (Context Diagram)
# =========================================================================
def make_fig3():
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    ax.axis('off')

    def entity_box(x, y, text):
        box = patches.Rectangle((x, y), 0.22, 0.18, fc='#ffffff', ec='#0f172a', lw=1.2)
        ax.add_patch(box)
        ax.text(x + 0.11, y + 0.09, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0f172a')

    # External Entities
    entity_box(0.04, 0.65, "User / Analyst\n(Client UI)")
    entity_box(0.04, 0.12, "Administrator\n(System Config)")
    entity_box(0.74, 0.40, "Camera / Media\n(Hardware/Files)")

    # Central Process
    center_circle = plt.Circle((0.45, 0.50), 0.16, fc='#f8fafc', ec='#0f172a', lw=1.5)
    ax.add_patch(center_circle)
    ax.text(0.45, 0.55, "0.0", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0f172a')
    ax.text(0.45, 0.47, "FaceForge\nVision System", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1e3a8a')

    # Data Store
    ds_box = patches.Rectangle((0.36, 0.10), 0.18, 0.12, fc='#f1f5f9', ec='#0f172a', lw=1)
    ax.add_patch(ds_box)
    ax.plot([0.36, 0.54], [0.10, 0.10], color='#0f172a', lw=1.5)
    ax.plot([0.36, 0.54], [0.22, 0.22], color='#0f172a', lw=1.5)
    ax.text(0.45, 0.16, "D1: results.csv", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0f172a')

    # Flows
    ax.annotate('Uploads & Stream', xy=(0.33, 0.60), xytext=(0.26, 0.70), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('Results & Analytics', xy=(0.26, 0.65), xytext=(0.33, 0.55), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('Config Flags', xy=(0.33, 0.42), xytext=(0.26, 0.22), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('Raw Media Frames', xy=(0.58, 0.52), xytext=(0.74, 0.52), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('Log Records', xy=(0.45, 0.23), xytext=(0.45, 0.34), arrowprops=dict(arrowstyle="->", lw=1))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig3_dfd_level0.png")

# =========================================================================
# Figure 4: DFD Level 1 (Four Modules)
# =========================================================================
def make_fig4():
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.axis('off')

    def proc_box(x, y, num, name, mod, color='#ffffff'):
        box = patches.FancyBboxPatch((x, y), 0.15, 0.22, boxstyle="round,pad=0.01", fc=color, ec='#0f172a', lw=1.2)
        ax.add_patch(box)
        ax.text(x + 0.075, y + 0.18, num, ha='center', va='center', fontsize=8, fontweight='bold', color='#1e3a8a')
        ax.text(x + 0.075, y + 0.11, name, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0f172a')
        ax.text(x + 0.075, y + 0.04, mod, ha='center', va='center', fontsize=6.8, color='#64748b')

    proc_box(0.04, 0.40, "1.0", "Media\nAcquisition", "Input Layer")
    proc_box(0.23, 0.40, "2.0", "Image\nPreprocessing", "Member 1 (Stub)", '#fffbeb')
    proc_box(0.42, 0.40, "3.0", "Face Detection\n& ROI Crop", "Member 2 (Stub)", '#fffbeb')
    proc_box(0.61, 0.40, "4.0", "Emotion\nInference", "Member 3 (Stub)", '#fffbeb')
    proc_box(0.80, 0.40, "5.0", "Storage &\nAnalytics", "Member 4 (Active)", '#ecfdf5')

    # Arrows
    for x in [0.19, 0.38, 0.57, 0.76]:
        ax.annotate('', xy=(x + 0.04, 0.51), xytext=(x, 0.51), arrowprops=dict(arrowstyle="->", lw=1.2, color='#0f172a'))

    # Data Store at bottom
    ds_box = patches.Rectangle((0.78, 0.08), 0.19, 0.15, fc='#f8fafc', ec='#0f172a', lw=1)
    ax.add_patch(ds_box)
    ax.text(0.875, 0.15, "D1: results.csv\n(Append Ledger)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0f172a')
    ax.annotate('Append Inferences', xy=(0.875, 0.24), xytext=(0.875, 0.40), arrowprops=dict(arrowstyle="->", lw=1.2, color='#059669'))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig4_dfd_level1.png")

# =========================================================================
# Figure 5: DFD Level 2 (Module 4 Pipeline & Telemetry Flow)
# =========================================================================
def make_fig5():
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.axis('off')

    def p_rect(x, y, w, h, title, sub):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", fc='#f8fafc', ec='#0f172a', lw=1)
        ax.add_patch(box)
        ax.text(x + w/2, y + h/2 + 0.02, title, ha='center', va='center', fontsize=7.5, fontweight='bold')
        ax.text(x + w/2, y + h/2 - 0.03, sub, ha='center', va='center', fontsize=6.5, color='#475569')

    p_rect(0.04, 0.60, 0.22, 0.25, "5.1 Route Dispatcher", "FastAPI app.py")
    p_rect(0.36, 0.60, 0.24, 0.25, "5.2 Pipeline Coordinator", "controller.py & Adapters")
    p_rect(0.70, 0.60, 0.24, 0.25, "5.3 Response Formatter", "Bounding Boxes + Confidence")
    p_rect(0.36, 0.15, 0.24, 0.25, "5.4 Telemetry Engine", "storage.py log_detection()")
    p_rect(0.70, 0.15, 0.24, 0.25, "5.5 Analytics Aggregator", "analytics.py Statistics")

    # Arrows
    ax.annotate('REST Call', xy=(0.36, 0.725), xytext=(0.26, 0.725), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('Inference Result', xy=(0.70, 0.725), xytext=(0.60, 0.725), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('Persist Data', xy=(0.48, 0.40), xytext=(0.48, 0.60), arrowprops=dict(arrowstyle="->", lw=1, color='#059669'))
    ax.annotate('Read Ledger', xy=(0.70, 0.275), xytext=(0.60, 0.275), arrowprops=dict(arrowstyle="->", lw=1))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig5_dfd_level2.png")

# =========================================================================
# Figure 6: Entity-Relationship / Telemetry Schema Diagram
# =========================================================================
def make_fig6():
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.axis('off')

    def entity_table(x, y, w, title, fields):
        h = 0.06 + len(fields)*0.035
        box = patches.FancyBboxPatch((x, y - h), w, h, boxstyle="square,pad=0", fc='#ffffff', ec='#0f172a', lw=1.2)
        ax.add_patch(box)
        # Header
        hdr = patches.Rectangle((x, y - 0.06), w, 0.06, fc='#f1f5f9', ec='#0f172a', lw=1)
        ax.add_patch(hdr)
        ax.text(x + w/2, y - 0.035, title, ha='center', va='center', fontsize=8, fontweight='bold', color='#0f172a')
        # Fields
        fy = y - 0.09
        for f in fields:
            ax.text(x + 0.02, fy, f, ha='left', va='center', fontsize=6.8, fontfamily='monospace', color='#334155')
            fy -= 0.035

    entity_table(0.05, 0.90, 0.28, "results.csv (Telemetry)", [
        "timestamp: VARCHAR(19)",
        "source: VARCHAR(10)",
        "file_name: VARCHAR(255)",
        "frame_number: INT",
        "face_id: INT",
        "emotion: VARCHAR(20)",
        "confidence: FLOAT",
        "status: VARCHAR(25)",
        "data_source: VARCHAR(10)"
    ])

    entity_table(0.40, 0.90, 0.26, "config.yaml (System Flags)", [
        "demo_mode: BOOLEAN",
        "use_module1: BOOLEAN",
        "use_module2: BOOLEAN",
        "use_module3: BOOLEAN",
        "confidence_threshold: FLOAT",
        "video_sampling_step: INT"
    ])

    entity_table(0.72, 0.90, 0.24, "analytics_summary", [
        "total_detections: INT",
        "dominant_emotion: VARCHAR",
        "average_confidence: FLOAT",
        "distribution: DICT",
        "timeline: LIST"
    ])

    # Connecting relations
    ax.annotate('Configures', xy=(0.40, 0.65), xytext=(0.33, 0.65), arrowprops=dict(arrowstyle="<->", lw=1, color='#64748b'))
    ax.annotate('Aggregates', xy=(0.72, 0.65), xytext=(0.33, 0.40), arrowprops=dict(arrowstyle="->", lw=1, color='#0284c7'))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig6_er_diagram.png")

# =========================================================================
# Figure 7: UML Class Diagram
# =========================================================================
def make_fig7():
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.axis('off')

    def uml_class(x, y, w, name, methods):
        h = 0.06 + len(methods)*0.032
        box = patches.Rectangle((x, y - h), w, h, fc='#ffffff', ec='#0f172a', lw=1.1)
        ax.add_patch(box)
        hdr = patches.Rectangle((x, y - 0.05), w, 0.05, fc='#f1f5f9', ec='#0f172a', lw=1)
        ax.add_patch(hdr)
        ax.text(x + w/2, y - 0.028, f"<<module>> {name}", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1e3a8a')
        cy = y - 0.075
        for m in methods:
            ax.text(x + 0.015, cy, m, ha='left', va='center', fontsize=6.5, fontfamily='monospace', color='#1e293b')
            cy -= 0.032

    uml_class(0.04, 0.92, 0.28, "controller.py", [
        "+ process_image(file_bytes, name)",
        "+ process_video_file(path, step)",
        "+ process_webcam_frame(bytes)",
        "+ load_config()",
        "+ save_config(dict)",
        "+ get_active_mode_badge()"
    ])

    uml_class(0.36, 0.92, 0.28, "storage.py", [
        "+ init_storage()",
        "+ log_detection(source, emotion..)",
        "+ load_results(source, emotion)",
        "+ clear_results()",
        "- RESULTS_FILE: Path"
    ])

    uml_class(0.68, 0.92, 0.28, "analytics.py", [
        "+ compute_analytics(df, filter)",
        "+ generate_distribution_chart(df)",
        "+ generate_timeline_chart(df)",
        "+ export_report_summary()"
    ])

    uml_class(0.20, 0.42, 0.26, "adapter_face.py (M2)", [
        "+ detect_faces(image)",
        "+ crop_face(image, box)",
        "+ read_video(path, step)"
    ])

    uml_class(0.52, 0.42, 0.26, "adapter_emotion.py (M3)", [
        "+ predict_face(face_roi)",
        "+ predict_frame(image)",
        "- CANONICAL_EMOTIONS: List"
    ])

    # Connectors
    ax.annotate('', xy=(0.36, 0.70), xytext=(0.32, 0.70), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('', xy=(0.68, 0.70), xytext=(0.64, 0.70), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('', xy=(0.33, 0.42), xytext=(0.20, 0.65), arrowprops=dict(arrowstyle="->", lw=1, linestyle='--'))
    ax.annotate('', xy=(0.55, 0.42), xytext=(0.30, 0.65), arrowprops=dict(arrowstyle="->", lw=1, linestyle='--'))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig7_class_diagram.png")

# =========================================================================
# Figure 8: Use Case Diagram (Main User Interactions)
# =========================================================================
def make_fig8():
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.axis('off')

    # Actor (Stick figure)
    ax.plot([0.12, 0.12], [0.55, 0.45], color='#0f172a', lw=1.5) # body
    ax.add_patch(plt.Circle((0.12, 0.60), 0.04, color='#0f172a', fill=False, lw=1.5)) # head
    ax.plot([0.08, 0.16], [0.51, 0.51], color='#0f172a', lw=1.5) # arms
    ax.plot([0.12, 0.08], [0.45, 0.36], color='#0f172a', lw=1.5) # left leg
    ax.plot([0.12, 0.16], [0.45, 0.36], color='#0f172a', lw=1.5) # right leg
    ax.text(0.12, 0.30, "User / Analyst", ha='center', va='center', fontsize=8, fontweight='bold')

    # System Boundary Box
    sys_box = patches.Rectangle((0.26, 0.08), 0.68, 0.84, fill=False, ec='#0f172a', lw=1.2)
    ax.add_patch(sys_box)
    ax.text(0.60, 0.88, "FaceForge Emotion System", ha='center', va='center', fontsize=9, fontweight='bold', color='#1e3a8a')

    # Use Case Ellipses
    cases = [
        ("Upload & Detect Image (UC-1)", 0.78),
        ("Process Video with Sampling (UC-2)", 0.65),
        ("Real-Time Webcam Streaming (UC-3)", 0.52),
        ("Filter & Download Results CSV (UC-4)", 0.39),
        ("View Analytics & Trends (UC-5)", 0.26),
        ("Configure Adapter Settings (UC-6)", 0.13),
    ]

    for title, y in cases:
        ellipse = patches.Ellipse((0.60, y), 0.44, 0.09, fc='#f8fafc', ec='#0f172a', lw=1)
        ax.add_patch(ellipse)
        ax.text(0.60, y, title, ha='center', va='center', fontsize=7.5, color='#0f172a')
        ax.plot([0.16, 0.38], [0.51, y], color='#475569', lw=0.9)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig8_use_case_main.png")

# =========================================================================
# Figure 9: Use Case Diagram (Video Sampling & Storage)
# =========================================================================
def make_fig9():
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.axis('off')

    # Actor: Video Processing Engine
    ax.text(0.12, 0.50, "<<subsystem>>\nVideo Engine", ha='center', va='center', fontsize=8, fontweight='bold', bbox=dict(boxstyle='square', fc='#f1f5f9'))

    # System boundary
    sys_box = patches.Rectangle((0.26, 0.10), 0.68, 0.80, fill=False, ec='#0f172a', lw=1.2)
    ax.add_patch(sys_box)
    ax.text(0.60, 0.85, "Telemetry & Frame Subsystem", ha='center', va='center', fontsize=9, fontweight='bold', color='#1e3a8a')

    # Ellipses with <<include>>
    e1 = patches.Ellipse((0.55, 0.68), 0.40, 0.09, fc='#f8fafc', ec='#0f172a', lw=1)
    ax.add_patch(e1)
    ax.text(0.55, 0.68, "Extract Video Frames", ha='center', va='center', fontsize=7.5)

    e2 = patches.Ellipse((0.55, 0.45), 0.40, 0.09, fc='#f8fafc', ec='#0f172a', lw=1)
    ax.add_patch(e2)
    ax.text(0.55, 0.45, "Apply Frame Sampling (N)", ha='center', va='center', fontsize=7.5)

    e3 = patches.Ellipse((0.55, 0.22), 0.40, 0.09, fc='#f8fafc', ec='#0f172a', lw=1)
    ax.add_patch(e3)
    ax.text(0.55, 0.22, "Append to results.csv", ha='center', va='center', fontsize=7.5)

    ax.annotate('<<include>>', xy=(0.55, 0.50), xytext=(0.55, 0.63), arrowprops=dict(arrowstyle="->", lw=1, linestyle='--'), ha='center', fontsize=6.5)
    ax.annotate('<<include>>', xy=(0.55, 0.27), xytext=(0.55, 0.40), arrowprops=dict(arrowstyle="->", lw=1, linestyle='--'), ha='center', fontsize=6.5)
    ax.plot([0.20, 0.35], [0.50, 0.68], color='#0f172a', lw=1)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig9_use_case_telemetry.png")

# =========================================================================
# Figure 10: Sequence Diagram
# =========================================================================
def make_fig10():
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.axis('off')

    lifelines = [
        ("User", 0.08),
        ("React UI", 0.25),
        ("FastAPI app", 0.45),
        ("Controller", 0.65),
        ("storage.py", 0.85)
    ]

    for name, x in lifelines:
        box = patches.Rectangle((x - 0.06, 0.88), 0.12, 0.06, fc='#f8fafc', ec='#0f172a', lw=1)
        ax.add_patch(box)
        ax.text(x, 0.91, name, ha='center', va='center', fontsize=7.5, fontweight='bold')
        ax.plot([x, x], [0.88, 0.08], color='#cbd5e1', lw=1, linestyle='--')

    # Sequence Messages
    msgs = [
        (0.08, 0.25, 0.80, "1. Select Image file"),
        (0.25, 0.45, 0.70, "2. POST /api/detect/image"),
        (0.45, 0.65, 0.60, "3. process_image()"),
        (0.65, 0.65, 0.50, "4. Detect Face & Predict"),
        (0.65, 0.85, 0.40, "5. log_detection(row)"),
        (0.85, 0.65, 0.32, "6. Append Confirmed"),
        (0.65, 0.45, 0.24, "7. Return result dict"),
        (0.45, 0.25, 0.16, "8. JSON {faces, boxes, emotion}"),
        (0.25, 0.08, 0.10, "9. Render Bounding Overlays")
    ]

    for x1, x2, y, txt in msgs:
        if x1 == x2:
            # Self call
            ax.annotate(txt, xy=(x1, y-0.03), xytext=(x1+0.08, y), arrowprops=dict(arrowstyle="->", lw=0.9), fontsize=6.8)
        else:
            is_ret = x2 < x1
            style = '--' if is_ret else '-'
            ax.annotate(txt, xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", lw=0.9, linestyle=style), fontsize=6.8)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig10_sequence_diagram.png")

# =========================================================================
# Figure 11: UML Component Diagram
# =========================================================================
def make_fig11():
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.axis('off')

    def cmp_box(x, y, w, h, name, tech):
        box = patches.Rectangle((x, y), w, h, fc='#ffffff', ec='#0f172a', lw=1.1)
        ax.add_patch(box)
        # Small component tabs on left
        ax.add_patch(patches.Rectangle((x - 0.012, y + h - 0.06), 0.024, 0.03, fc='#f1f5f9', ec='#0f172a', lw=0.8))
        ax.add_patch(patches.Rectangle((x - 0.012, y + h - 0.11), 0.024, 0.03, fc='#f1f5f9', ec='#0f172a', lw=0.8))
        ax.text(x + w/2, y + h/2 + 0.02, name, ha='center', va='center', fontsize=8, fontweight='bold', color='#1e3a8a')
        ax.text(x + w/2, y + h/2 - 0.03, tech, ha='center', va='center', fontsize=6.8, color='#475569')

    cmp_box(0.05, 0.60, 0.24, 0.28, "<<component>>\nReact SPA", "Vite Frontend (Port 5173)")
    cmp_box(0.38, 0.60, 0.24, 0.28, "<<component>>\nAPI Gateway", "FastAPI app.py (Port 8000)")
    cmp_box(0.71, 0.60, 0.24, 0.28, "<<component>>\nPipeline Core", "controller.py Dispatcher")

    cmp_box(0.15, 0.12, 0.28, 0.28, "<<component>>\nStorage Engine", "storage.py & results.csv")
    cmp_box(0.55, 0.12, 0.30, 0.28, "<<component>>\nModular Adapters", "Preprocess, Face, Emotion (M1..3)")

    # Connectors
    ax.annotate('HTTP / REST', xy=(0.38, 0.74), xytext=(0.29, 0.74), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('Internal Call', xy=(0.71, 0.74), xytext=(0.62, 0.74), arrowprops=dict(arrowstyle="->", lw=1))
    ax.annotate('Append / Read', xy=(0.42, 0.60), xytext=(0.29, 0.40), arrowprops=dict(arrowstyle="->", lw=1, color='#059669'))
    ax.annotate('Invokes Adapters', xy=(0.71, 0.40), xytext=(0.83, 0.60), arrowprops=dict(arrowstyle="->", lw=1))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig11_component_diagram.png")

if __name__ == "__main__":
    print("Generating all 11 FaceForge SRS diagrams...")
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    make_fig5()
    make_fig6()
    make_fig7()
    make_fig8()
    make_fig9()
    make_fig10()
    make_fig11()
    print("All 11 diagrams created successfully in srs_diagrams/ folder!")

