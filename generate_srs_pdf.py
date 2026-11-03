"""
generate_srs_pdf.py
===================
Generates a formal academic Software Requirements Specification (SRS) PDF for
FaceForge, conforming to the 4-Member Collaborative Implementation Roadmap.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 762, "FaceForge — Software Requirements Specification (SRS) | 4-Member Implementation")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, 756, 576, 756)

        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 25, page_str)
        self.drawString(36, 25, "Confidential & Academic — Final Year Project | SRS Group G2 IT")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 35, 576, 35)
        self.restoreState()

def build_pdf():
    pdf_filename = "FaceForge_SRS_Specification.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a')
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4338ca')
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#64748b')
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=14,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#1e293b')
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155'),
        leftIndent=14
    )

    stub_box_style = ParagraphStyle(
        'StubBox',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#b45309')
    )

    active_box_style = ParagraphStyle(
        'ActiveBox',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#065f46')
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )

    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )

    td_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Title Block
    story.append(Paragraph("SOFTWARE REQUIREMENTS SPECIFICATION (SRS)", title_style))
    story.append(Paragraph("<b>FaceForge:</b> Multi-Modal Facial Emotion Recognition System (Image &bull; Video &bull; Real-Time Webcam)", subtitle_style))
    story.append(Paragraph("Academic Year 2026-27 &bull; Final Year Engineering Project &bull; Collaborative 4-Member Team Structure", meta_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#4f46e5'), spaceBefore=2, spaceAfter=10))

    # Document Control Table
    story.append(Paragraph("1. Document Control & Responsibility Allocation", h1_style))
    doc_table_data = [
        [Paragraph("Team Member", th_style), Paragraph("Module / Role", th_style), Paragraph("Core Technical Responsibility", th_style), Paragraph("Status in SRS", th_style)],
        [
            Paragraph("<b>Member 1</b>", td_style),
            Paragraph("Module 1: Preprocessing", td_style),
            Paragraph("Dataset collection (FER-2013), data partitioning, grayscale conversion, image resizing, and normalization.", td_style),
            Paragraph("<font color='#b45309'><b>Template Stub</b><br/>(To be filled by M1)</font>", td_style)
        ],
        [
            Paragraph("<b>Member 2</b>", td_style),
            Paragraph("Module 2: Computer Vision", td_style),
            Paragraph("OpenCV pipeline, face localization (x, y, w, h), ROI face cropping, multi-face handling, and video frame extraction.", td_style),
            Paragraph("<font color='#b45309'><b>Template Stub</b><br/>(To be filled by M2)</font>", td_style)
        ],
        [
            Paragraph("<b>Member 3</b>", td_style),
            Paragraph("Module 3: Emotion Model", td_style),
            Paragraph("Pretrained FER model integration, 7 emotion probabilities, evaluation metrics (F1, Precision, Recall), and confusion matrix.", td_style),
            Paragraph("<font color='#b45309'><b>Template Stub</b><br/>(To be filled by M3)</font>", td_style)
        ],
        [
            Paragraph("<b>Member 4<br/>(Active)</b>", td_style),
            Paragraph("<b>Module 4: Integration & UI</b>", td_style),
            Paragraph("Full application entrypoint (app.py), REST API Gateway, light Web UI, CSV storage engine (results.csv), and analytics dashboard.", td_style),
            Paragraph("<font color='#059669'><b>100% Fully Built &amp;<br/>Specified</b></font>", td_style)
        ],
    ]
    t_control = Table(doc_table_data, colWidths=[65, 95, 260, 120])
    t_control.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_control)
    story.append(Spacer(1, 10))

    # Section 2: Project Overview & Core Concept
    story.append(Paragraph("2. Project Overview & Scope", h1_style))
    story.append(Paragraph(
        "FaceForge is an engineering-grade computer vision and machine learning application developed to recognize human affective states from visual input. "
        "The system processes visual media, detects human faces, isolates facial regions of interest (ROI), and classifies emotions using an established pretrained deep learning model. "
        "The project is purposefully architected as a collaborative 4-part system so that each team member operates within a clearly decoupled module with strict input/output contracts.",
        body_style
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Three Operating Modes Supported:</b>", h2_style))
    story.append(Paragraph("&bull; <b>Mode 1 (Static Image):</b> Single-photo analysis with face bounding box overlays and confidence scores.", bullet_style))
    story.append(Paragraph("&bull; <b>Mode 2 (Video File):</b> Offline video analysis with configurable frame sampling step to optimize computational throughput.", bullet_style))
    story.append(Paragraph("&bull; <b>Mode 3 (Live Webcam):</b> Real-time browser camera stream inference via OpenCV/Webcam capture with live overlay telemetry.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 3: Four-Layer Architecture
    story.append(Paragraph("3. Four-Layer System Architecture", h1_style))
    arch_data = [
        [Paragraph("Layer", th_style), Paragraph("Primary Function", th_style), Paragraph("Component Technologies", th_style), Paragraph("Owner", th_style)],
        [
            Paragraph("<b>Layer 1: Input</b>", td_style),
            Paragraph("Data acquisition from Image uploads, Video files, and live camera feed.", td_style),
            Paragraph("OpenCV VideoCapture, HTML5 File API, MediaDevices", td_style),
            Paragraph("Member 2 &amp; 4", td_style)
        ],
        [
            Paragraph("<b>Layer 2: Vision</b>", td_style),
            Paragraph("Preprocessing, face detection (bounding coordinates), and ROI extraction.", td_style),
            Paragraph("OpenCV, NumPy matrix slicing, Haar / Deep Detector", td_style),
            Paragraph("Member 1 &amp; 2", td_style)
        ],
        [
            Paragraph("<b>Layer 3: AI Inference</b>", td_style),
            Paragraph("Pretrained model inference returning 7 emotion probability vectors.", td_style),
            Paragraph("FER Library (Pretrained CNN), Softmax argmax", td_style),
            Paragraph("Member 3", td_style)
        ],
        [
            Paragraph("<b>Layer 4: Integration</b>", td_style),
            Paragraph("Web UI, REST API Gateway, append-only CSV ledger, and analytics.", td_style),
            Paragraph("FastAPI, React (Light UI), pandas, matplotlib, storage.py", td_style),
            Paragraph("Member 4", td_style)
        ],
    ]
    t_arch = Table(arch_data, colWidths=[90, 200, 160, 90])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # Section 4: Module Stubs for Members 1, 2, 3
    story.append(Paragraph("4. Teammate Module Specifications (Modules 1, 2 & 3)", h1_style))

    # Module 1 Stub Box
    story.append(Paragraph("<b>4.1 Module 1: Dataset & Preprocessing (Member 1)</b>", h2_style))
    m1_box = [
        [Paragraph(
            "<b>[SECTION ALLOCATED TO MEMBER 1]</b><br/>"
            "&bull; <b>Input:</b> Raw static images and FER-2013 directory partitions.<br/>"
            "&bull; <b>Output Contract:</b> Preprocessed normalized grayscale/RGB NumPy image array.<br/>"
            "&bull; <b>Tasks to complete:</b> Document dataset class distribution (Happy, Sad, Angry, etc.), resizing parameters, "
            "grayscale transformations, normalization equations, and test set partitioning in <code>dataset_analysis.py</code>.",
            stub_box_style
        )]
    ]
    t_m1 = Table(m1_box, colWidths=[540])
    t_m1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#fde68a')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_m1)
    story.append(Spacer(1, 6))

    # Module 2 Stub Box
    story.append(Paragraph("<b>4.2 Module 2: Computer Vision & Face Detection (Member 2)</b>", h2_style))
    m2_box = [
        [Paragraph(
            "<b>[SECTION ALLOCATED TO MEMBER 2]</b><br/>"
            "&bull; <b>Input:</b> Image matrix or video stream frame.<br/>"
            "&bull; <b>Output Contract:</b> Face bounding box coordinates <code>(x, y, w, h)</code> and extracted face ROI array <code>image[y:y+h, x:x+w]</code>.<br/>"
            "&bull; <b>Tasks to complete:</b> Document face detection algorithms, multiple face loop handling, video frame sampling mechanics "
            "(<code>frame_count % 10 == 0</code>), and camera stream FPS stabilization in <code>face_detection.py</code> and <code>video_processor.py</code>.",
            stub_box_style
        )]
    ]
    t_m2 = Table(m2_box, colWidths=[540])
    t_m2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#fde68a')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_m2)
    story.append(Spacer(1, 6))

    # Module 3 Stub Box
    story.append(Paragraph("<b>4.3 Module 3: Pretrained Emotion Model & Evaluation (Member 3)</b>", h2_style))
    m3_box = [
        [Paragraph(
            "<b>[SECTION ALLOCATED TO MEMBER 3]</b><br/>"
            "&bull; <b>Input:</b> Cropped face ROI image array.<br/>"
            "&bull; <b>Output Contract:</b> 7-class probability dictionary and dominant emotion label with confidence scalar.<br/>"
            "&bull; <b>Tasks to complete:</b> Document pretrained FER deep learning model architecture, benchmark accuracy on test partitions, "
            "generate 7x7 confusion matrix (<code>confusion_matrix.png</code>), and calculate Precision, Recall, and F1-Scores in <code>metrics_report.txt</code>.",
            stub_box_style
        )]
    ]
    t_m3 = Table(m3_box, colWidths=[540])
    t_m3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fffbeb')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#fde68a')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_m3)
    story.append(Spacer(1, 12))

    # Section 5: Module 4 Complete Specification
    story.append(Paragraph("5. Module 4: Integration, Web UI, Storage & Analytics (Full Implementation)", h1_style))
    story.append(Paragraph(
        "Module 4 represents the centralized integration hub and customer-facing software suite. "
        "It coordinates all pipeline stages, enforces non-crashing execution using graceful mock adapters, records all detections into persistent storage, "
        "and presents an enterprise-grade light-themed user interface.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # REST API Table
    story.append(Paragraph("<b>5.1 RESTful API Gateway Specification (`app.py`)</b>", h2_style))
    api_data = [
        [Paragraph("Endpoint", th_style), Paragraph("Method", th_style), Paragraph("Input Parameters", th_style), Paragraph("Output Response / Schema", th_style)],
        [
            Paragraph("<code>/api/health</code>", td_style),
            Paragraph("GET", td_style),
            Paragraph("None", td_style),
            Paragraph("System status badge, active adapter mode, documentation URL.", td_style)
        ],
        [
            Paragraph("<code>/api/config</code>", td_style),
            Paragraph("GET / POST", td_style),
            Paragraph("JSON payload with feature flags (demo_mode, use_module1..3, sampling_step)", td_style),
            Paragraph("Updated configuration parameters, saved to config.yaml.", td_style)
        ],
        [
            Paragraph("<code>/api/detect/image</code>", td_style),
            Paragraph("POST", td_style),
            Paragraph("Multipart form file (JPG / PNG)", td_style),
            Paragraph("Bounding coordinates, detected emotions, confidence, and annotated preview.", td_style)
        ],
        [
            Paragraph("<code>/api/detect/video</code>", td_style),
            Paragraph("POST", td_style),
            Paragraph("Multipart video file (MP4 / AVI), sampling_step integer", td_style),
            Paragraph("Total frames processed, emotion sequence timeline, per-frame detections.", td_style)
        ],
        [
            Paragraph("<code>/api/detect/webcam-frame</code>", td_style),
            Paragraph("POST", td_style),
            Paragraph("Base64 image string or multipart frame", td_style),
            Paragraph("Live dominant emotion tag, confidence percentage, status pill.", td_style)
        ],
        [
            Paragraph("<code>/api/results</code>", td_style),
            Paragraph("GET", td_style),
            Paragraph("Query filters: source, emotion, data_source", td_style),
            Paragraph("Filtered rows from results.csv, total record count.", td_style)
        ],
        [
            Paragraph("<code>/api/results/download</code>", td_style),
            Paragraph("GET", td_style),
            Paragraph("None", td_style),
            Paragraph("Direct file download of results.csv ledger archive.", td_style)
        ],
        [
            Paragraph("<code>/api/results/clear</code>", td_style),
            Paragraph("DELETE", td_style),
            Paragraph("None", td_style),
            Paragraph("Empties results.csv after user confirmation.", td_style)
        ],
        [
            Paragraph("<code>/api/analytics</code>", td_style),
            Paragraph("GET", td_style),
            Paragraph("Query filter: data_source (all/live/demo)", td_style),
            Paragraph("Aggregated statistical counts, class distribution, mean confidence.", td_style)
        ],
        [
            Paragraph("<code>/api/evaluation</code>", td_style),
            Paragraph("GET", td_style),
            Paragraph("None", td_style),
            Paragraph("Returns metrics_report.txt content and confusion_matrix.png base64.", td_style)
        ],
    ]
    t_api = Table(api_data, colWidths=[130, 50, 160, 200])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 8))

    # 5.2 Telemetry Storage Schema
    story.append(Paragraph("<b>5.2 Telemetry Storage Schema (`storage.py` &rarr; `results.csv`)</b>", h2_style))
    story.append(Paragraph(
        "All predictions across Image, Video, and Webcam modes are automatically logged into an append-only persistent CSV file with the following column structure:",
        body_style
    ))
    story.append(Spacer(1, 3))
    csv_data = [
        [Paragraph("Field Name", th_style), Paragraph("Type", th_style), Paragraph("Description", th_style), Paragraph("Sample Value", th_style)],
        [Paragraph("timestamp", td_style), Paragraph("String", td_style), Paragraph("Timestamp of detection event", td_style), Paragraph("2026-10-31 19:39:24", td_style)],
        [Paragraph("source", td_style), Paragraph("String", td_style), Paragraph("Medium: image, video, or webcam", td_style), Paragraph("webcam", td_style)],
        [Paragraph("file_name", td_style), Paragraph("String", td_style), Paragraph("Uploaded file or camera stream index", td_style), Paragraph("camera_0", td_style)],
        [Paragraph("frame_number", td_style), Paragraph("Integer", td_style), Paragraph("Frame index in video sequence", td_style), Paragraph("140", td_style)],
        [Paragraph("face_id", td_style), Paragraph("Integer", td_style), Paragraph("Index of face in multi-face frame", td_style), Paragraph("0", td_style)],
        [Paragraph("emotion", td_style), Paragraph("String", td_style), Paragraph("Classified dominant emotion", td_style), Paragraph("Happy", td_style)],
        [Paragraph("confidence", td_style), Paragraph("Float", td_style), Paragraph("Normalized model probability [0, 1]", td_style), Paragraph("0.92", td_style)],
        [Paragraph("status", td_style), Paragraph("String", td_style), Paragraph("High-level status tag", td_style), Paragraph("Happy", td_style)],
        [Paragraph("data_source", td_style), Paragraph("String", td_style), Paragraph("Provenance: live or demo mock", td_style), Paragraph("live", td_style)],
    ]
    t_csv = Table(csv_data, colWidths=[80, 50, 260, 150])
    t_csv.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_csv)
    story.append(Spacer(1, 8))

    # 5.3 Web UI Screen Breakdown
    story.append(Paragraph("<b>5.3 Light-Themed Web User Interface (`frontend/src/`)</b>", h2_style))
    story.append(Paragraph("&bull; <b>Design System:</b> Clean Slate light theme (`#f8fafc` canvas, `#ffffff` cards, `#0f172a` text, `#4f46e5` electric indigo primary).", bullet_style))
    story.append(Paragraph("&bull; <b>Home View (`HomeView.jsx`):</b> System architecture summary, active pipeline status pill, and direct one-click mode launches.", bullet_style))
    story.append(Paragraph("&bull; <b>Image Detection View (`ImageView.jsx`):</b> Drag-and-drop file upload, preview rendering, and bounding box results table.", bullet_style))
    story.append(Paragraph("&bull; <b>Video Detection View (`VideoView.jsx`):</b> HTML5 video player, interactive step-sampling range slider, and frame progress bar.", bullet_style))
    story.append(Paragraph("&bull; <b>Webcam Detection View (`WebcamView.jsx`):</b> Camera stream with start/stop triggers and floating real-time emotion telemetry badge.", bullet_style))
    story.append(Paragraph("&bull; <b>Results Ledger (`ResultsView.jsx`):</b> Tabular display with multi-level filtering (source, emotion, data tier) and CSV export.", bullet_style))
    story.append(Paragraph("&bull; <b>Analytics Dashboard (`AnalyticsView.jsx`):</b> Statistical frequency chart, valence spread, mean confidence, and PDF summary.", bullet_style))
    story.append(Paragraph("&bull; <b>Settings View (`SettingsView.jsx`):</b> Independent toggles for teammate adapters (Modules 1, 2, and 3) and threshold controls.", bullet_style))
    story.append(Paragraph("&bull; <b>Model Evaluation View (`EvaluationView.jsx`):</b> Displays Member 3's confusion matrix and parsed F1/Recall metrics report.", bullet_style))
    story.append(Spacer(1, 10))

    # Section 6: Master Testing Matrix
    story.append(Paragraph("6. Master Verification & Testing Suite", h1_style))
    test_data = [
        [Paragraph("Test ID", th_style), Paragraph("Mode", th_style), Paragraph("Input Condition", th_style), Paragraph("Expected System Outcome", th_style), Paragraph("Lead", th_style)],
        [Paragraph("T1", td_style), Paragraph("Image", td_style), Paragraph("Clear portrait with smile", td_style), Paragraph("Face detected, bounded, tagged Happy with &gt;75% confidence.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T2", td_style), Paragraph("Image", td_style), Paragraph("Sad portrait", td_style), Paragraph("Classified Sad, entry appended to results.csv.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T3", td_style), Paragraph("Image", td_style), Paragraph("Angry expression", td_style), Paragraph("Classified Angry, probability distribution updated.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T4", td_style), Paragraph("Image", td_style), Paragraph("Neutral face", td_style), Paragraph("Classified Neutral, displayed in results table.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T5", td_style), Paragraph("Image", td_style), Paragraph("Multiple faces in frame", td_style), Paragraph("All distinct faces bounded and classified individually.", td_style), Paragraph("M2/M4", td_style)],
        [Paragraph("T6", td_style), Paragraph("Image", td_style), Paragraph("Scenery without human faces", td_style), Paragraph("Reports 0 faces detected without throwing server error.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T7", td_style), Paragraph("Image", td_style), Paragraph("Dark / low-lighting image", td_style), Paragraph("System triggers low-confidence warning badge gracefully.", td_style), Paragraph("M1/M4", td_style)],
        [Paragraph("T8", td_style), Paragraph("Video", td_style), Paragraph("10-second MP4 clip", td_style), Paragraph("Frames extracted according to step N, progress bar renders.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T9", td_style), Paragraph("Video", td_style), Paragraph("Multi-person video", td_style), Paragraph("Tracks detections across sampled frames sequentially.", td_style), Paragraph("M2/M4", td_style)],
        [Paragraph("T10", td_style), Paragraph("Video", td_style), Paragraph("Subject changing emotions", td_style), Paragraph("Analytics timeline shows temporal emotional transitions.", td_style), Paragraph("M3/M4", td_style)],
        [Paragraph("T11", td_style), Paragraph("Video", td_style), Paragraph("Low-resource hardware (i3)", td_style), Paragraph("Frame sampling skips intermediate frames, preventing lag.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T12", td_style), Paragraph("Webcam", td_style), Paragraph("Normal ambient lighting", td_style), Paragraph("Real-time live video feed with floating prediction HUD.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T13", td_style), Paragraph("Webcam", td_style), Paragraph("Dim ambient room", td_style), Paragraph("Video feed continues without camera disconnect.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T14", td_style), Paragraph("Webcam", td_style), Paragraph("Subject turns away from camera", td_style), Paragraph("HUD shows No Face Detected gracefully without crash.", td_style), Paragraph("M4", td_style)],
        [Paragraph("T15", td_style), Paragraph("Storage", td_style), Paragraph("Reset database action", td_style), Paragraph("Requires modal confirmation, then safely clears results.csv.", td_style), Paragraph("M4", td_style)],
    ]
    t_test = Table(test_data, colWidths=[40, 50, 140, 260, 50])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 10))

    # Section 7: Conclusion
    story.append(Paragraph("7. Limitations & Conclusion", h1_style))
    story.append(Paragraph(
        "<b>Limitations:</b> Processing speed is bounded by CPU clock frequencies when analyzing videos at 100% frame density. "
        "The system mitigates this via frame sampling steps. Furthermore, deep shadows or extreme camera angles reduce face localization accuracy.<br/><br/>"
        "<b>Conclusion:</b> The FaceForge project establishes a robust modular architecture for affective computing. "
        "By clearly demarcating responsibilities into 4 modules, Members 1, 2, and 3 are provided standardized interfaces to plug in their datasets, "
        "detectors, and evaluation models, while Member 4 provides the operational, scalable web integration, persistent ledger, and visualization engine.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"SRS PDF successfully generated: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
