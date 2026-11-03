"""
generate_team_srs_pdf.py
========================
Generates a formal academic Software Requirements Specification (SRS) PDF for
FaceForge, matching Team B's SKIT RTU format, layout, revision tables,
table of contents, headers, footers, diagrams, and section structure.
Reflects Member 4's complete technical implementation with template stubs
for Members 1, 2, and 3.
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
    KeepTogether,
    PageBreak
)
from reportlab.pdfgen import canvas

class SKITCanvas(canvas.Canvas):
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
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Outer Border Box on every page (like Team B format)
        self.setStrokeColor(colors.HexColor("#334155"))
        self.setLineWidth(1)
        self.rect(30, 24, 552, 744)

        if self._pageNumber > 1:
            # Header Block Table Box
            self.setStrokeColor(colors.HexColor("#475569"))
            self.setLineWidth(0.75)
            self.rect(50, 715, 512, 36)
            self.line(400, 715, 400, 751)
            self.line(50, 733, 562, 733)

            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0f172a"))
            self.drawString(56, 739, "FaceForge — Multi-Modal Facial Emotion Recognition System")
            self.drawString(406, 739, "Version: 2.0")

            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(56, 721, "Software Requirements Specification (SRS) &bull; Module 4 Integration")
            self.drawString(406, 721, "Date: 31/10/2026 | ID: 2026-27-IT-G2")

            # Footer
            self.setFont("Helvetica", 8.5)
            self.setFillColor(colors.HexColor("#0f172a"))
            self.drawCentredString(306, 34, f"{self._pageNumber}")
            
        self.restoreState()


def build_srs_pdf():
    pdf_filename = "FaceForge_Final_Year_SRS_TeamB_Format.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=88,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Academic Typographical Hierarchy
    cover_code_style = ParagraphStyle(
        'CoverCode', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=14,
        alignment=2, textColor=colors.HexColor('#0f172a')
    )

    cover_title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=23,
        alignment=1, textColor=colors.HexColor('#0f172a'), spaceBefore=35, spaceAfter=14
    )

    cover_doc_type = ParagraphStyle(
        'CoverDocType', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        alignment=1, textColor=colors.HexColor('#1e3a8a'), spaceAfter=8
    )

    cover_ver_style = ParagraphStyle(
        'CoverVer', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=15,
        alignment=1, textColor=colors.HexColor('#334155'), spaceAfter=22
    )

    cover_sub_desc = ParagraphStyle(
        'CoverSubDesc', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=14,
        alignment=1, textColor=colors.HexColor('#1e293b'), spaceAfter=45
    )

    h1_style = ParagraphStyle(
        'H1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=colors.HexColor('#0f172a'), spaceBefore=14, spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'H2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=14,
        textColor=colors.HexColor('#0f172a'), spaceBefore=10, spaceAfter=4
    )

    h3_style = ParagraphStyle(
        'H3', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.8, leading=12,
        textColor=colors.HexColor('#1e3a8a'), spaceBefore=6, spaceAfter=3
    )

    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12.5,
        textColor=colors.HexColor('#1e293b'), spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12.5,
        textColor=colors.HexColor('#1e293b'), leftIndent=12, spaceAfter=2.5
    )

    stub_callout = ParagraphStyle(
        'StubCallout', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11.5,
        textColor=colors.HexColor('#92400e')
    )

    th_style = ParagraphStyle(
        'TH', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.5, leading=10,
        textColor=colors.HexColor('#0f172a'), alignment=0
    )

    td_style = ParagraphStyle(
        'TD', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.2, leading=9.5,
        textColor=colors.HexColor('#1e293b'), alignment=0
    )

    code_block = ParagraphStyle(
        'CodeBlock', parent=styles['Normal'],
        fontName='Courier', fontSize=6.8, leading=9,
        textColor=colors.HexColor('#0f172a')
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE (Team B / SKIT RTU Format)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>2026-27-IT-G2</b>", cover_code_style))
    story.append(Spacer(1, 15))

    # Institute Monogram / Seal representation
    story.append(Paragraph("<font color='#b91c1c' size=13><b>[ SKIT ]</b></font><br/><font color='#475569' size=7>ESTD. 2000</font>", ParagraphStyle('LogoTxt', parent=styles['Normal'], alignment=0)))
    story.append(Spacer(1, 35))

    story.append(Paragraph("FaceForge: Multi-Modal Facial Emotion Recognition and Analytical Telemetry System", cover_title_style))
    story.append(Paragraph("Software Requirements Specification", cover_doc_type))
    story.append(Paragraph("Version 2.0", cover_ver_style))
    story.append(Paragraph(
        "Submitted in Partial Fulfillment for the Award of Degree of Bachelor of Technology in Information Technology from Rajasthan Technical University, Kota",
        cover_sub_desc
    ))

    # Attribution Grid: Mentor, Coordinator, Submitted By
    attrib_data = [
        [
            Paragraph("<b>MENTOR:</b><br/>Dr. / Prof. Faculty Mentor<br/>Dept. of Information Technology", body_style),
            Paragraph("<b>SUBMITTED BY:</b><br/><b>Member 4 (Lead Integrator & UI)</b><br/>Roll No: 23ESKITXXX<br/><i>In collaboration with Members 1, 2 & 3</i>", body_style)
        ],
        [
            Paragraph("<b>COORDINATOR:</b><br/>Project Coordinator<br/>Dept. of Information Technology", body_style),
            Paragraph("<b>PROJECT ID:</b> 2026-27-IT-G2<br/><b>TRACK:</b> Computer Vision & Web Systems", body_style)
        ]
    ]
    t_attrib = Table(attrib_data, colWidths=[250, 260])
    t_attrib.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
    ]))
    story.append(t_attrib)
    story.append(Spacer(1, 40))

    # Department Footer
    dept_style = ParagraphStyle('DeptStyle', parent=styles['Normal'], alignment=1, fontName='Helvetica-Bold', fontSize=9, leading=13, textColor=colors.HexColor('#0f172a'))
    story.append(Paragraph("DEPARTMENT OF INFORMATION TECHNOLOGY", dept_style))
    story.append(Paragraph("SWAMI KESHWANAND INSTITUTE OF TECHNOLOGY, MANAGEMENT & GRAMOTHAN", ParagraphStyle('InstSub', parent=dept_style, fontSize=8.5, leading=12)))
    story.append(Paragraph("(An Autonomous Institute Affiliated to Rajasthan Technical University, Kota)", ParagraphStyle('Affil', parent=styles['Normal'], alignment=1, fontSize=7.5, leading=11, textColor=colors.HexColor('#475569'))))
    story.append(Paragraph("Ramnagaria (Jagatpura), Jaipur &ndash; 302017", ParagraphStyle('Addr', parent=styles['Normal'], alignment=1, fontSize=8, leading=12, textColor=colors.HexColor('#1e293b'))))
    story.append(Paragraph("<b>SESSION 2026&ndash;27</b>", ParagraphStyle('Sess', parent=dept_style, fontSize=9, leading=13, spaceBefore=4)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: REVISION HISTORY TABLE
    # =========================================================================
    story.append(Paragraph("Revision History", ParagraphStyle('RevHead', parent=h1_style, alignment=1, fontSize=13, spaceAfter=14)))
    
    rev_data = [
        [Paragraph("Date", th_style), Paragraph("Version", th_style), Paragraph("Description", th_style), Paragraph("Author", th_style)],
        [
            Paragraph("20/07/2026", td_style),
            Paragraph("0.1", td_style),
            Paragraph("Initial requirement analysis, 4-member pipeline formulation, and system scope.", td_style),
            Paragraph("Member 4", td_style)
        ],
        [
            Paragraph("01/10/2026", td_style),
            Paragraph("1.0", td_style),
            Paragraph("Draft SRS specifications with input/output contracts for Members 1, 2, and 3.", td_style),
            Paragraph("Member 4", td_style)
        ],
        [
            Paragraph("31/10/2026", td_style),
            Paragraph("2.0", td_style),
            Paragraph("Revised SRS with complete Module 4 implementation (FastAPI backend, React Light UI, persistent results.csv storage, analytics suite, and test matrix).", td_style),
            Paragraph("Member 4", td_style)
        ],
    ]
    t_rev = Table(rev_data, colWidths=[70, 45, 290, 95])
    t_rev.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#334155')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_rev)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: TABLE OF CONTENTS (Exact Team B Section Breakdown)
    # =========================================================================
    story.append(Paragraph("Table of Contents", ParagraphStyle('TOCHead', parent=h1_style, alignment=1, fontSize=14, spaceAfter=16)))

    toc_items = [
        ("1  Introduction", "1"),
        ("    1.1 Purpose", "1"),
        ("    1.2 Motivation", "1"),
        ("    1.3 Tools and Technologies", "1"),
        ("    1.4 References", "2"),
        ("2  Market Survey", "3"),
        ("    2.1 Objectives", "3"),
        ("    2.2 Unexplored Areas", "3"),
        ("    2.3 Comparative Study of Similar Solutions", "4"),
        ("3  Requirements", "5"),
        ("    3.1 Functional Requirements", "5"),
        ("    3.2 Non-Functional Requirements", "5"),
        ("    3.3 Hardware Requirements", "6"),
        ("    3.4 Software Requirements", "6"),
        ("    3.5 Agile Model", "7"),
        ("    3.6 Business Process Model", "7"),
        ("    3.7 Supplementary Requirements", "8"),
        ("4  System Architecture", "9"),
        ("    4.1 Client-Server & 4-Layer Architecture", "9"),
        ("    4.2 Communications Interfaces", "9"),
        ("5  Design and Implementation", "10"),
        ("    5.1 Product Features & 4-Member Division", "10"),
        ("    5.2 Data Flow Diagrams (Level 0, 1 & 2)", "11"),
        ("    5.3 E-R & Telemetry Storage Diagram", "14"),
        ("    5.4 Class Diagram Design", "14"),
        ("    5.5 Use Case Diagrams", "15"),
        ("    5.6 Sequence Diagram", "18"),
        ("    5.7 Component Diagram", "19"),
        ("6  Conclusion and Future Scope", "20"),
        ("7  Mapping with UN Sustainable Development Goals", "21"),
    ]

    toc_table_data = []
    for title, page in toc_items:
        is_main = not title.startswith("    ")
        f_name = 'Helvetica-Bold' if is_main else 'Helvetica'
        f_size = 8.5 if is_main else 8.0
        c_val = '#0f172a' if is_main else '#334155'
        p_title = Paragraph(f"<font color='{c_val}'>{title}</font>", ParagraphStyle('TOCT', parent=styles['Normal'], fontName=f_name, fontSize=f_size, leading=12))
        p_page = Paragraph(f"<font color='{c_val}'>{page}</font>", ParagraphStyle('TOCP', parent=styles['Normal'], fontName=f_name, fontSize=f_size, leading=12, alignment=2))
        toc_table_data.append([p_title, p_page])

    t_toc = Table(toc_table_data, colWidths=[450, 50])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.HexColor('#f1f5f9')),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: INTRODUCTION
    # =========================================================================
    story.append(Paragraph("1  Introduction", h1_style))
    story.append(Paragraph("1.1 Purpose", h2_style))
    story.append(Paragraph(
        "The purpose of this Software Requirements Specification (SRS) is to describe the technical architecture, "
        "system requirements, and implementation specifications for the multi-modal facial emotion recognition suite named <b>FaceForge</b>. "
        "The system is an engineering application designed to detect human faces, isolate facial regions of interest (ROI), and classify affective expressions "
        "from three operating inputs: static photographs, video files, and real-time live browser webcam streams.<br/><br/>"
        "The application is structured into four distinct modules to facilitate collaborative development across four team members. "
        "This specification is maintained by <b>Member 4</b> (Lead Integrator & UI Engineer) and provides complete operational specifications for the integration platform, "
        "while providing formal input/output interface contracts for Member 1 (Preprocessing), Member 2 (Computer Vision), and Member 3 (Emotion Model).",
        body_style
    ))

    story.append(Paragraph("1.2 Motivation", h2_style))
    story.append(Paragraph(
        "Non-verbal affective cues, particularly facial expressions, represent over 55% of human interpersonal communication. "
        "While deep learning has made substantial strides in computer vision, deploying emotion recognition in practical applications remains challenging due to "
        "high computational latency on low-end hardware, lack of clean cross-platform web interfaces, and absent historical telemetry logging.<br/><br/>"
        "FaceForge addresses these barriers by combining OpenCV frame-sampling optimization, a pretrained facial expression model, an append-only telemetry storage ledger, "
        "and an accessible modern web interface. Rather than requiring users to install complex local Python environments, FaceForge provides an immediate, browser-accessible "
        "platform for affective analysis.",
        body_style
    ))

    story.append(Paragraph("1.3 Tools and Technologies", h2_style))
    story.append(Paragraph("The following tools and frameworks constitute the FaceForge tech stack:", body_style))
    story.append(Paragraph("&bull; <b>Frontend (UI / Presentation Layer):</b> React 19, Vite, Vanilla CSS design tokens (Light theme), Lucide Icons.", bullet_style))
    story.append(Paragraph("&bull; <b>Backend &amp; API Gateway:</b> Python 3.11, FastAPI, Uvicorn ASGI server, Starlette StaticFiles.", bullet_style))
    story.append(Paragraph("&bull; <b>Computer Vision &amp; Image Processing:</b> OpenCV (cv2), NumPy array manipulation, Pillow (PIL).", bullet_style))
    story.append(Paragraph("&bull; <b>Machine Learning &amp; Emotion Engine:</b> Pretrained FER Deep Learning Model (CNN), Softmax activation.", bullet_style))
    story.append(Paragraph("&bull; <b>Storage &amp; Telemetry:</b> Append-only CSV storage engine (`storage.py` &rarr; `results/results.csv`), PyYAML.", bullet_style))
    story.append(Paragraph("&bull; <b>Analytics &amp; Visualization:</b> pandas, matplotlib, ReportLab PDF compilation.", bullet_style))

    story.append(Paragraph("1.4 References", h2_style))
    story.append(Paragraph("1. Goodfellow, I., et al., <i>Challenges in Representation Learning: Facial Expression Recognition</i>, ICML, 2013.", bullet_style))
    story.append(Paragraph("2. OpenCV Open Source Computer Vision Library: https://opencv.org/", bullet_style))
    story.append(Paragraph("3. FastAPI Framework Documentation: https://fastapi.tiangolo.com/", bullet_style))
    story.append(Paragraph("4. React Documentation: https://react.dev/", bullet_style))
    story.append(Paragraph("5. IEEE Std 830-1998, <i>IEEE Recommended Practice for Software Requirements Specifications</i>.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: MARKET SURVEY
    # =========================================================================
    story.append(Paragraph("2  Market Survey", h1_style))
    story.append(Paragraph("2.1 Objectives", h2_style))
    story.append(Paragraph(
        "The primary objectives of the market survey are: (1) To evaluate existing facial analysis toolkits; (2) To understand how pretrained deep learning networks "
        "perform on varied video sampling rates; (3) To identify pain points in multi-modal desktop applications; and (4) To contrast FaceForge against commercial and open-source benchmarks.",
        body_style
    ))

    story.append(Paragraph("2.2 Unexplored Areas", h2_style))
    story.append(Paragraph(
        "While several facial emotion models exist on GitHub and HuggingFace, most existing tools are isolated Python scripts or Jupyter notebooks lacking practical deployment features: "
        "<br/>&bull; <b>Unified Multi-Modal Input:</b> Few systems seamlessly support Image, offline Video file sampling, and live browser camera streaming in one UI."
        "<br/>&bull; <b>Historical Telemetry Logging:</b> Predictions are rarely preserved in queryable, structured CSV formats."
        "<br/>&bull; <b>Lightweight Browser UI:</b> Existing tools often mandate heavier desktop GUI libraries (Tkinter/PyQt) rather than modern responsive web interfaces.",
        body_style
    ))

    story.append(Paragraph("2.3 Comparative Study of Similar Solutions", h2_style))
    comp_data = [
        [Paragraph("Feature / Capability", th_style), Paragraph("Standard FER Scripts", th_style), Paragraph("DeepFace / Commercial", th_style), Paragraph("FaceForge (Our System)", th_style)],
        [
            Paragraph("Primary Interface", td_style),
            Paragraph("CLI / OpenCV window", td_style),
            Paragraph("Proprietary Cloud API", td_style),
            Paragraph("Modern React Light Web UI (HMR)", td_style)
        ],
        [
            Paragraph("Multi-Modal Support", td_style),
            Paragraph("Static image only", td_style),
            Paragraph("Image / Cloud Video", td_style),
            Paragraph("Image, Video (Step Sampling), Webcam", td_style)
        ],
        [
            Paragraph("Local Execution &amp; Privacy", td_style),
            Paragraph("Local terminal only", td_style),
            Paragraph("Cloud upload required", td_style),
            Paragraph("100% On-Premise / Local Host", td_style)
        ],
        [
            Paragraph("Persistent Telemetry", td_style),
            Paragraph("Console print only", td_style),
            Paragraph("Cloud dashboard database", td_style),
            Paragraph("Append-only results.csv ledger", td_style)
        ],
        [
            Paragraph("Analytics Visualizer", td_style),
            Paragraph("None", td_style),
            Paragraph("Aggregated analytics", td_style),
            Paragraph("Distribution charts &amp; PDF reports", td_style)
        ],
        [
            Paragraph("Collaborative Modularity", td_style),
            Paragraph("Monolithic single script", td_style),
            Paragraph("Closed-source black box", td_style),
            Paragraph("4-Module Decoupled Architecture", td_style)
        ]
    ]
    t_comp = Table(comp_data, colWidths=[105, 120, 125, 150])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#334155')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: REQUIREMENTS
    # =========================================================================
    story.append(Paragraph("3  Requirements", h1_style))
    story.append(Paragraph("3.1 Functional Requirements (FRs)", h2_style))
    story.append(Paragraph("&bull; <b>FR-1 (Image Emotion Detection):</b> The system shall accept JPG and PNG image uploads, locate faces, render bounding boxes, and output the dominant emotion and confidence.", bullet_style))
    story.append(Paragraph("&bull; <b>FR-2 (Video Frame Sampling):</b> The system shall process MP4 and AVI files by sampling every N-th frame (configurable 1-30) to reduce computation time while logging frame indices.", bullet_style))
    story.append(Paragraph("&bull; <b>FR-3 (Real-Time Webcam Analysis):</b> The system shall capture live camera frames via the browser, evaluate facial emotions, and display a live floating HUD with active emotion and probability.", bullet_style))
    story.append(Paragraph("&bull; <b>FR-4 (Persistent Telemetry Logging):</b> All inferences across all three modes shall be logged into `results/results.csv` with timestamp, source, frame number, face ID, emotion, and confidence.", bullet_style))
    story.append(Paragraph("&bull; <b>FR-5 (Analytics &amp; Statistics Engine):</b> The system shall calculate class frequencies across the 7 emotions, average confidence, and temporal affective timelines.", bullet_style))
    story.append(Paragraph("&bull; <b>FR-6 (Config &amp; Adapter Isolation):</b> The system shall provide feature toggles in `config.yaml` allowing mock adapters for Members 1, 2, and 3 to be enabled/disabled independently without crashing.", bullet_style))

    story.append(Paragraph("3.2 Non-Functional Requirements (NFRs)", h2_style))
    story.append(Paragraph("&bull; <b>Performance &amp; Latency:</b> Single static image analysis shall complete in < 800 ms. Video processing with sampling step 10 shall maintain throughput > 20 FPS equivalent.", bullet_style))
    story.append(Paragraph("&bull; <b>Usability &amp; Design:</b> The user interface shall employ a clean light color palette with WCAG AA compliance and accessible high-contrast text.", bullet_style))
    story.append(Paragraph("&bull; <b>Fault Tolerance &amp; Robustness:</b> Detection requests with no faces or corrupt files shall return readable HTTP error messages without crashing the server process.", bullet_style))
    story.append(Paragraph("&bull; <b>Data Integrity:</b> Storage operations shall append atomically to prevent file corruption during simultaneous requests.", bullet_style))

    story.append(Paragraph("3.3 Hardware Requirements", h2_style))
    story.append(Paragraph("&bull; <b>Development / Host System:</b> Intel Core i3 / AMD Ryzen 3 or higher, minimum 4 GB RAM, 2 GB free disk space.", bullet_style))
    story.append(Paragraph("&bull; <b>Video Capture Device:</b> Integrated HD webcam or external USB camera supporting 720p / 30 FPS.", bullet_style))

    story.append(Paragraph("3.4 Software Requirements", h2_style))
    story.append(Paragraph("&bull; <b>Operating System:</b> Windows 10/11, Ubuntu 20.04+, or macOS.", bullet_style))
    story.append(Paragraph("&bull; <b>Runtime Environments:</b> Python 3.10+ and Node.js v18+ with npm.", bullet_style))
    story.append(Paragraph("&bull; <b>Core Libraries:</b> FastAPI, Uvicorn, OpenCV-Python, Pandas, Matplotlib, ReportLab.", bullet_style))

    story.append(Paragraph("3.5 Agile Model", h2_style))
    story.append(Paragraph(
        "FaceForge follows an iterative Agile lifecycle partitioned into 2-week sprints: Sprint 1 (Skeleton & Mock Adapters), "
        "Sprint 2 (REST API & Storage Engine), Sprint 3 (React UI & Light Theme), Sprint 4 (Analytics & Evaluation Integration), and Sprint 5 (Final Testing & Verification).",
        body_style
    ))

    story.append(Paragraph("3.6 Business Process Model", h2_style))
    story.append(Paragraph(
        "1. User accesses web portal &rarr; 2. Selects input mode (Image/Video/Webcam) &rarr; 3. System acquires visual data &rarr; "
        "4. Preprocessing prepares matrix &rarr; 5. Face detector extracts bounding boxes &rarr; 6. Pretrained FER outputs emotion vector &rarr; "
        "7. Results appended to CSV ledger &rarr; 8. Visual overlays and analytics updated.",
        body_style
    ))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 4: SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("4  System Architecture", h1_style))
    story.append(Paragraph("4.1 Client-Server & 4-Layer Architecture", h2_style))
    story.append(Paragraph(
        "FaceForge employs a decoupled client-server architecture consisting of a React Single-Page Application (SPA) client, "
        "a FastAPI backend application server, a persistent file-based CSV telemetry store, and modular adapter pipelines. "
        "The architecture is organized across four collaborative layers:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Layer 1 (Input Layer):</b> Interfaces with user files (Image/Video) and client camera devices.", bullet_style))
    story.append(Paragraph("&bull; <b>Layer 2 (Computer Vision Layer):</b> OpenCV matrix decoding, resizing, grayscale, face ROI cropping.", bullet_style))
    story.append(Paragraph("&bull; <b>Layer 3 (AI / Emotion Layer):</b> Pretrained FER model generating probability distributions across 7 emotions.", bullet_style))
    story.append(Paragraph("&bull; <b>Layer 4 (Integration & UI Layer):</b> FastAPI API Gateway, React UI, results storage, and analytics visualizer.", bullet_style))

    story.append(Paragraph("4.2 Communications Interfaces", h2_style))
    story.append(Paragraph("&bull; <b>Client-Server REST APIs:</b> HTTP/1.1 JSON-based exchange between React frontend and FastAPI on port 8000.", bullet_style))
    story.append(Paragraph("&bull; <b>File Upload Protocol:</b> Multipart form-data encoding for image and video transfers.", bullet_style))
    story.append(Paragraph("&bull; <b>Webcam Streaming Protocol:</b> Canvas frame capture with base64/binary POST streaming.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 5: DESIGN AND IMPLEMENTATION (4-MEMBER BREAKDOWN)
    # =========================================================================
    story.append(Paragraph("5  Design and Implementation", h1_style))
    story.append(Paragraph("5.1 Product Features & 4-Member Collaborative Division", h2_style))

    # Member 1 Box
    story.append(Paragraph("<b>5.1.1 Module 1: Preprocessing & Dataset Specifications (Member 1)</b>", h3_style))
    m1_callout = [
        [Paragraph(
            "<b>[ALLOCATED RESPONSIBILITY: MEMBER 1 &mdash; DATASET &amp; PREPROCESSING]</b><br/>"
            "&bull; <b>Input Contract:</b> Raw visual media &amp; FER-2013 directory partitions.<br/>"
            "&bull; <b>Output Contract:</b> Cleaned, normalized, resized grayscale/RGB image matrices.<br/>"
            "&bull; <i>Status:</i> Interface contract established in <code>adapter_preprocess.py</code>. "
            "Member 1 is responsible for populating specific dataset partition statistics, histogram equalization parameters, and tensor normalization formulas.",
            stub_callout
        )]
    ]
    t_m1 = Table(m1_callout, colWidths=[500])
    t_m1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fffbeb')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#fde68a')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_m1)
    story.append(Spacer(1, 5))

    # Member 2 Box
    story.append(Paragraph("<b>5.1.2 Module 2: Computer Vision & Face Detection Specifications (Member 2)</b>", h3_style))
    m2_callout = [
        [Paragraph(
            "<b>[ALLOCATED RESPONSIBILITY: MEMBER 2 &mdash; COMPUTER VISION &amp; DETECTION]</b><br/>"
            "&bull; <b>Input Contract:</b> Decoded image matrix or video stream frame from OpenCV.<br/>"
            "&bull; <b>Output Contract:</b> Face bounding box coordinates <code>(x, y, w, h)</code> and cropped face ROI <code>image[y:y+h, x:x+w]</code>.<br/>"
            "&bull; <i>Status:</i> Interface contract established in <code>adapter_face.py</code>. "
            "Member 2 is responsible for finalizing the face detector model, multi-face array loops, video frame sampling mechanics, and camera FPS stabilization.",
            stub_callout
        )]
    ]
    t_m2 = Table(m2_callout, colWidths=[500])
    t_m2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fffbeb')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#fde68a')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_m2)
    story.append(Spacer(1, 5))

    # Member 3 Box
    story.append(Paragraph("<b>5.1.3 Module 3: Pretrained Emotion Model & Evaluation Specifications (Member 3)</b>", h3_style))
    m3_callout = [
        [Paragraph(
            "<b>[ALLOCATED RESPONSIBILITY: MEMBER 3 &mdash; PRETRAINED MODEL &amp; EVALUATION]</b><br/>"
            "&bull; <b>Input Contract:</b> Extracted face ROI matrix.<br/>"
            "&bull; <b>Output Contract:</b> 7-class emotion probabilities and dominant label with confidence score.<br/>"
            "&bull; <i>Status:</i> Interface contract established in <code>adapter_emotion.py</code>. "
            "Member 3 is responsible for integrating the pretrained FER network, generating <code>confusion_matrix.png</code>, and compiling Precision/Recall/F1 in <code>metrics_report.txt</code>.",
            stub_callout
        )]
    ]
    t_m3 = Table(m3_callout, colWidths=[500])
    t_m3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fffbeb')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#fde68a')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_m3)
    story.append(Spacer(1, 5))

    # Member 4 Box (Full Details)
    story.append(Paragraph("<b>5.1.4 Module 4: System Integration, UI, Storage & Analytics (Member 4 &mdash; Fully Active)</b>", h3_style))
    m4_callout = [
        [Paragraph(
            "<b>[ALLOCATED RESPONSIBILITY: MEMBER 4 &mdash; FULLY IMPLEMENTED &amp; ACTIVE]</b><br/>"
            "&bull; <b>Application Orchestrator (`app.py`):</b> Central FastAPI server exposing 10 REST endpoints with CORS and static SPA mounting.<br/>"
            "&bull; <b>Light-Themed Web UI (`frontend/`):</b> Responsive React interface covering Home, Image, Video, Webcam, Results Ledger, and Analytics Dashboard.<br/>"
            "&bull; <b>Telemetry Ledger Engine (`storage.py`):</b> Append-only storage writing detections to <code>results/results.csv</code> with filter/export/clear operations.<br/>"
            "&bull; <b>Statistical Analytics Visualizer (`analytics.py`):</b> Computes class distribution, temporal valence tracking, and mean confidence vectors.",
            ParagraphStyle('ActiveText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11.5, textColor=colors.HexColor('#065f46'))
        )]
    ]
    t_m4 = Table(m4_callout, colWidths=[500])
    t_m4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ecfdf5')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#a7f3d0')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_m4)
    story.append(Spacer(1, 10))

    # 5.2 Data Flow Diagrams
    story.append(Paragraph("5.2 Data Flow Diagrams (DFDs)", h2_style))
    story.append(Paragraph("<b>DFD Level 0 (Context Diagram):</b>", h3_style))
    story.append(Paragraph(
        "<code>[User / Client] &harr; (Input: Image/Video/Webcam) &harr; [0.0 FaceForge Vision System] &harr; (Output: Overlays, CSV Records, Analytics Charts)</code>",
        code_block
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>DFD Level 1 (Major Subsystems):</b>", h3_style))
    story.append(Paragraph(
        "<code>[User] &rarr; [1.0 Media Acquisition] &rarr; [2.0 Preprocessing (M1)] &rarr; [3.0 Face Detection (M2)] &rarr; [4.0 Emotion Inference (M3)] &rarr; [5.0 Storage &amp; Analytics (M4)] &rarr; [results.csv]</code>",
        code_block
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>DFD Level 2 (Module 4 Pipeline &amp; Storage Flow):</b>", h3_style))
    story.append(Paragraph(
        "<code>[API Route: /api/detect/*] &rarr; [controller.py Dispatcher] &rarr; [Mock/Live Adapters] &rarr; [storage.log_detection()] &rarr; [results.csv] &rarr; [analytics.compute_analytics()] &rarr; [React UI View]</code>",
        code_block
    ))
    story.append(Spacer(1, 10))

    # 5.3 E-R / Data Schema Diagram
    story.append(Paragraph("5.3 Entity-Relationship & Telemetry Storage Schema (`storage.py`)", h2_style))
    story.append(Paragraph("The primary persistent entity is the inference record appended to `results.csv`:", body_style))
    
    schema_data = [
        [Paragraph("Attribute", th_style), Paragraph("Data Type", th_style), Paragraph("Constraints", th_style), Paragraph("Description", th_style)],
        [Paragraph("timestamp", td_style), Paragraph("VARCHAR(19)", td_style), Paragraph("NOT NULL", td_style), Paragraph("Format: YYYY-MM-DD HH:MM:SS", td_style)],
        [Paragraph("source", td_style), Paragraph("VARCHAR(10)", td_style), Paragraph("CHECK(source IN ('image','video','webcam'))", td_style), Paragraph("Input medium category", td_style)],
        [Paragraph("file_name", td_style), Paragraph("VARCHAR(255)", td_style), Paragraph("NOT NULL", td_style), Paragraph("Source file name or camera index", td_style)],
        [Paragraph("frame_number", td_style), Paragraph("INTEGER", td_style), Paragraph("DEFAULT 0", td_style), Paragraph("Frame index in video sequence", td_style)],
        [Paragraph("face_id", td_style), Paragraph("INTEGER", td_style), Paragraph("DEFAULT 0", td_style), Paragraph("Index of face in multi-face frame", td_style)],
        [Paragraph("emotion", td_style), Paragraph("VARCHAR(20)", td_style), Paragraph("NOT NULL", td_style), Paragraph("Classified expression label", td_style)],
        [Paragraph("confidence", td_style), Paragraph("FLOAT", td_style), Paragraph("CHECK(confidence BETWEEN 0 AND 1)", td_style), Paragraph("Model probability scalar", td_style)],
        [Paragraph("status", td_style), Paragraph("VARCHAR(25)", td_style), Paragraph("NOT NULL", td_style), Paragraph("Affective group: Happy, Neutral, etc.", td_style)],
        [Paragraph("data_source", td_style), Paragraph("VARCHAR(10)", td_style), Paragraph("CHECK(data_source IN ('live','demo'))", td_style), Paragraph("Data provenance flag", td_style)],
    ]
    t_sch = Table(schema_data, colWidths=[80, 75, 175, 170])
    t_sch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_sch)
    story.append(Spacer(1, 10))

    # 5.4 Class Diagram
    story.append(Paragraph("5.4 Class & Modular Component Architecture", h2_style))
    story.append(Paragraph(
        "The Python backend is structured into decoupled modules: "
        "<br/>&bull; <code>controller.py</code>: Coordinates pipeline execution, loads configuration, annotates images with bounding boxes."
        "<br/>&bull; <code>storage.py</code>: Manages CSV initialization, atomic appending, filtering, and resetting."
        "<br/>&bull; <code>analytics.py</code>: Performs pandas aggregations, computes class distributions, and creates matplotlib figures."
        "<br/>&bull; <code>adapter_preprocess.py, adapter_face.py, adapter_emotion.py</code>: Teammate adapter boundary wrappers.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # 5.5 Use Case & Sequence
    story.append(Paragraph("5.5 Use Case & Sequence Workflow", h2_style))
    story.append(Paragraph(
        "<b>Primary Use Cases:</b> (1) UC-1: Upload &amp; Analyze Image; (2) UC-2: Process Video File with Frame Sampling; "
        "(3) UC-3: Stream Live Webcam Inference; (4) UC-4: Filter &amp; Export Results CSV; (5) UC-5: Generate Analytics PDF Report; "
        "(6) UC-6: Configure Adapters &amp; Confidence Thresholds.<br/><br/>"
        "<b>Sequence of Operations:</b> Client uploads file &rarr; FastAPI receives multipart request &rarr; Controller dispatches to Preprocess Adapter (M1) &rarr; "
        "Face Detector Adapter (M2) locates bounding box &rarr; Emotion Adapter (M3) evaluates face &rarr; Storage Engine records row to CSV &rarr; JSON returned to React UI &rarr; Bounding box rendered on canvas.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 6: CONCLUSION AND FUTURE SCOPE
    # =========================================================================
    story.append(Paragraph("6  Conclusion and Future Scope", h1_style))
    story.append(Paragraph(
        "<b>Conclusion:</b> FaceForge provides an enterprise-ready affective vision architecture. "
        "By clearly establishing decoupled module boundaries, Members 1, 2, and 3 are enabled to test and plug in their datasets, "
        "detectors, and evaluation models independently, while Member 4 delivers a fully functional web application, persistent storage ledger, "
        "and analytical reporting suite.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Future Scope:</b> (1) Custom model fine-tuning on domain-specific emotional expressions; (2) GPU CUDA acceleration for multi-stream 60 FPS feeds; "
        "(3) Docker containerization for one-click cross-platform deployment; (4) Mobile camera PWA support.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 7: MAPPING WITH UN SDGS (Exact Team B Section 7 format)
    # =========================================================================
    story.append(Paragraph("7  Mapping with UN Sustainable Development Goals", h1_style))
    story.append(Paragraph("The following table maps FaceForge to the United Nations Sustainable Development Goals (SDGs):", body_style))

    sdg_data = [
        [Paragraph("SDG No.", th_style), Paragraph("SDG Title", th_style), Paragraph("Relevance to FaceForge Project", th_style)],
        [
            Paragraph("<b>SDG 3</b>", td_style),
            Paragraph("Good Health and Well-being", td_style),
            Paragraph("Facial expression monitoring can provide non-invasive clinical mental health screening, stress detection, and patient affective state tracking.", td_style)
        ],
        [
            Paragraph("<b>SDG 4</b>", td_style),
            Paragraph("Quality Education", td_style),
            Paragraph("Enables automated learner engagement analysis in virtual and physical classrooms, alerting educators to student confusion or disinterest.", td_style)
        ],
        [
            Paragraph("<b>SDG 9</b>", td_style),
            Paragraph("Industry, Innovation, and Infrastructure", td_style),
            Paragraph("Applies digital innovation by uniting computer vision, pretrained neural networks, and modular web architecture on accessible desktop hardware.", td_style)
        ],
        [
            Paragraph("<b>SDG 10</b>", td_style),
            Paragraph("Reduced Inequalities", td_style),
            Paragraph("The browser-based light UI provides open access to affective computing tools without requiring expensive cloud subscriptions or proprietary hardware.", td_style)
        ],
    ]
    t_sdg = Table(sdg_data, colWidths=[65, 135, 300])
    t_sdg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#334155')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sdg)

    doc.build(story, canvasmaker=SKITCanvas)
    print(f"Generated Team B-format SRS PDF: {pdf_filename}")

if __name__ == "__main__":
    build_srs_pdf()
