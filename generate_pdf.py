"""
Generates a formal academic integration specification PDF for FaceForge teammates.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether

def generate_pdf():
    pdf_filename = "FaceForge_Teammate_Integration_Guide.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e3a8a')
    )

    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )

    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )

    code_style = ParagraphStyle(
        'DocCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f1f5f9'),
        borderPadding=6
    )

    elements = []

    # Title Banner
    elements.append(Paragraph("FACEFORGE: TEAM INTEGRATION & CODE SPECIFICATION GUIDE", header_style))
    elements.append(Paragraph("<b>Final Year B.Tech IT (2026-27) · Group G2</b> | Project Module 4 Integration Contract", sub_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1e3a8a'), spaceAfter=12))

    # Introduction Box
    intro_text = (
        "<b>Notice to Teammates (Modules 1, 2, and 3):</b><br/>"
        "Module 4 (Frontend User Interface, CSV Result Logging, Analytics Engine, and Adapter Shell) has been "
        "fully completed. To plug your code into the application without altering the UI or database, "
        "simply ensure your module matches the exact inputs and outputs specified below."
    )
    elements.append(Paragraph(intro_text, body_style))
    elements.append(Spacer(1, 10))

    # Architecture Overview Table
    table_data = [
        ["Module & Role", "Responsible Teammate", "Assigned File", "Adapter Integration File"],
        ["Module 1: Preprocessing", "Teammate 1", "module1_preprocess.py", "adapter_preprocess.py"],
        ["Module 2: Face Detection", "Teammate 2", "module2_detection.py", "adapter_face.py"],
        ["Module 3: Emotion Model", "Teammate 3", "module3_model.py + weights", "adapter_emotion.py"],
        ["Module 4: UI, Storage, Analytics", "Module 4 Owner", "app.py, storage.py, analytics.py", "Fully Active (Complete)"]
    ]
    t = Table(table_data, colWidths=[150, 110, 140, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('TOPPADDING', (0,1), (-1,-1), 4),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 14))

    # SECTION 1: Teammate 1
    elements.append(Paragraph("1. TEAMMATE 1 — MODULE 1 (IMAGE PREPROCESSING)", section_heading))
    elements.append(Paragraph(
        "<b>Goal:</b> Take an input BGR image frame and apply your preprocessing pipeline (e.g., resizing, histogram equalization, noise reduction).<br/>"
        "<b>Delivery File:</b> <code>module1_preprocess.py</code> in the project root.",
        body_style
    ))
    m1_code = (
        "# module1_preprocess.py<br/>"
        "import cv2<br/>"
        "import numpy as np<br/><br/>"
        "def preprocess_image(img: np.ndarray) -> np.ndarray:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'''<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Input: img (NumPy ndarray in BGR format from OpenCV)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Output: preprocessed img (NumPy ndarray, BGR format)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'''<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;# Your processing logic here...<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;return img"
    )
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(m1_code, code_style))
    elements.append(Spacer(1, 10))

    # SECTION 2: Teammate 2
    elements.append(Paragraph("2. TEAMMATE 2 — MODULE 2 (FACE DETECTION & FRAMING)", section_heading))
    elements.append(Paragraph(
        "<b>Goal:</b> Detect all faces in a BGR image frame and return bounding box coordinates.<br/>"
        "<b>Delivery File:</b> <code>module2_detection.py</code> in the project root.",
        body_style
    ))
    m2_code = (
        "# module2_detection.py<br/>"
        "import cv2<br/>"
        "from typing import List, Tuple<br/><br/>"
        "def find_faces(img) -> List[Tuple[int, int, int, int]]:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'''<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Input: BGR image ndarray<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Output: List of (x, y, w, h) bounding box coordinates<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Example: [(120, 80, 200, 200)]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'''<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;# Your Haar / YOLO / MTCNN detector logic here...<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;return boxes"
    )
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(m2_code, code_style))
    elements.append(Spacer(1, 10))

    # SECTION 3: Teammate 3
    elements.append(Paragraph("3. TEAMMATE 3 — MODULE 3 (EMOTION CLASSIFIER MODEL)", section_heading))
    elements.append(Paragraph(
        "<b>Goal:</b> Classify a cropped face image into 7 emotion classes and produce probability scores.<br/>"
        "<b>Delivery Files:</b> <code>module3_model.py</code>, model weights (e.g. <code>.h5</code>/<code>.keras</code>/<code>.pt</code>), "
        "and evaluation files in <code>results/metrics_report.txt</code> and <code>results/confusion_matrix.png</code>.<br/>"
        "<b>Required 7 Classes:</b> <code>angry, disgust, fear, happy, sad, surprise, neutral</code>",
        body_style
    ))
    m3_code = (
        "# module3_model.py<br/>"
        "from typing import Dict<br/><br/>"
        "def predict_emotion(face_crop) -> Dict[str, float]:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'''<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Input: NumPy array of a cropped face<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Output: Dict of 7 probabilities that sum to ~1.0<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Example: {'angry': 0.05, 'disgust': 0.01, 'fear': 0.02, 'happy': 0.82,<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'sad': 0.03, 'surprise': 0.02, 'neutral': 0.05}<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;'''<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;# Your model.predict(face_crop) logic here...<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;return scores"
    )
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(m3_code, code_style))
    elements.append(Spacer(1, 10))

    # SECTION 4: Integration Checklist
    elements.append(Paragraph("4. HOW TO TEST AND PLUG IN YOUR MODULE", section_heading))
    checklist_text = (
        "<b>Step 1:</b> Put your <code>.py</code> script and model files into the <code>FaceForge/</code> root folder.<br/>"
        "<b>Step 2:</b> Open your corresponding adapter file (<code>adapter_preprocess.py</code>, <code>adapter_face.py</code>, or <code>adapter_emotion.py</code>).<br/>"
        "<b>Step 3:</b> Import your function inside the adapter and return your results in the contract format.<br/>"
        "<b>Step 4:</b> In <code>config.yaml</code>, switch your flag from <code>false</code> to <code>true</code> (e.g., <code>use_module2: true</code>).<br/>"
        "<b>Step 5:</b> Run <code>python app.py</code> and check the UI at <code>http://localhost:8000</code>. If any import errors occur, the adapter will safely log a warning without crashing."
    )
    elements.append(Paragraph(checklist_text, body_style))
    elements.append(Spacer(1, 12))

    # Footer note
    footer = Paragraph(
        "<b>Prepared by:</b> Module 4 Owner (Integration & UI) · FaceForge Group G2 (2026-27)",
        ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor('#64748b'))
    )
    elements.append(footer)

    doc.build(elements)
    print(f"Generated PDF: {pdf_filename}")

if __name__ == "__main__":
    generate_pdf()
