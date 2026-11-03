"""
generate_exact_teamb_srs_pdf.py
===============================
Produces a 24-page Software Requirements Specification (SRS) for FaceForge
matching Team B's SKIT RTU format, layout, and visual design.
Includes all 11 generated architectural and UML diagrams.
Saves directly to Desktop as requested.
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
    PageBreak,
    Image as RLImage
)
from reportlab.pdfgen import canvas

DESKTOP_PDF_PATH = r"C:\Users\web\OneDrive\Desktop\FaceForge_SRS_Final.pdf"
LOCAL_PDF_PATH = "FaceForge_SRS_Final.pdf"
DIAGRAM_DIR = "srs_diagrams"

class ExactTeamBCanvas(canvas.Canvas):
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
        
        # Outer Border Box on EVERY page (Exact Team B format)
        self.setStrokeColor(colors.HexColor("#334155"))
        self.setLineWidth(1)
        self.rect(36, 26, 540, 740)

        # Running Header on page >= 2
        if self._pageNumber >= 2:
            # Header Box Table (500 width)
            hx, hy, hw, hh = 50, 706, 512, 36
            self.setStrokeColor(colors.HexColor("#475569"))
            self.setLineWidth(0.75)
            self.rect(hx, hy, hw, hh)
            self.line(hx + 355, hy, hx + 355, hy + hh) # vertical divide
            self.line(hx, hy + 18, hx + hw, hy + 18)    # horizontal divide

            # Top Left
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0f172a"))
            self.drawString(hx + 6, hy + 23, "FaceForge — Multi-Modal Facial Emotion Recognition System")
            
            # Top Right
            self.drawString(hx + 361, hy + 23, "Version: 2.0")

            # Bottom Left
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(hx + 6, hy + 6, "Software Requirements Specification &bull; Module 4 Integration")

            # Bottom Right
            self.drawString(hx + 361, hy + 6, "Date: 31/10/2026 | ID: 2026-27-IT-G2")

            # Bottom Page Number
            self.setFont("Helvetica", 8.5)
            self.setFillColor(colors.HexColor("#0f172a"))
            self.drawCentredString(306, 36, f"{self._pageNumber}")
            
        self.restoreState()


def build_exact_pdf():
    # Build locally first
    doc = SimpleDocTemplate(
        LOCAL_PDF_PATH,
        pagesize=letter,
        rightMargin=48,
        leftMargin=48,
        topMargin=95,    # Clears 742pt header box cleanly with breathing room
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Academic Typography Styles matching Team B
    cover_code = ParagraphStyle('CoverCode', fontName='Helvetica-Bold', fontSize=10, leading=14, alignment=2, textColor=colors.HexColor('#0f172a'))
    cover_title = ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=16.5, leading=22, alignment=1, textColor=colors.HexColor('#0f172a'), spaceBefore=25, spaceAfter=14)
    cover_doc = ParagraphStyle('CoverDoc', fontName='Helvetica-Bold', fontSize=13, leading=17, alignment=1, textColor=colors.HexColor('#1e3a8a'), spaceAfter=8)
    cover_ver = ParagraphStyle('CoverVer', fontName='Helvetica-Bold', fontSize=11, leading=15, alignment=1, textColor=colors.HexColor('#334155'), spaceAfter=20)
    cover_desc = ParagraphStyle('CoverDesc', fontName='Helvetica', fontSize=9.5, leading=14, alignment=1, textColor=colors.HexColor('#1e293b'), spaceAfter=35)
    
    h1_style = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#0f172a'), spaceBefore=12, spaceAfter=6)
    h2_style = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#0f172a'), spaceBefore=8, spaceAfter=4)
    h3_style = ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=colors.HexColor('#1e3a8a'), spaceBefore=6, spaceAfter=3)
    
    body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=colors.HexColor('#1e293b'), spaceAfter=5)
    bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=colors.HexColor('#1e293b'), leftIndent=12, spaceAfter=3)
    caption = ParagraphStyle('Caption', fontName='Helvetica-Bold', fontSize=8, leading=11, alignment=1, textColor=colors.HexColor('#334155'), spaceBefore=4, spaceAfter=8)

    th_style = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=colors.HexColor('#0f172a'))
    td_style = ParagraphStyle('TD', fontName='Helvetica', fontSize=7.2, leading=9.5, textColor=colors.HexColor('#1e293b'))

    stub_box = ParagraphStyle('StubBox', fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=colors.HexColor('#92400e'))
    active_box = ParagraphStyle('ActiveBox', fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=colors.HexColor('#065f46'))

    def load_img(fname, w=440, h=220):
        path = os.path.join(DIAGRAM_DIR, fname)
        if os.path.exists(path):
            return RLImage(path, width=w, height=h)
        return Paragraph(f"[Diagram: {fname}]", body)

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>2026-27-IT-G2</b>", cover_code))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<font color='#b91c1c' size=14><b>[ SKIT ]</b></font><br/><font color='#64748b' size=7.5>ESTD. 2000</font>", ParagraphStyle('LogoTxt', parent=styles['Normal'], alignment=0)))
    story.append(Spacer(1, 25))
    story.append(Paragraph("FaceForge: Multi-Modal Facial Emotion Recognition and Analytical Telemetry System", cover_title))
    story.append(Paragraph("Software Requirements Specification", cover_doc))
    story.append(Paragraph("Version 2.0", cover_ver))
    story.append(Paragraph("Submitted in Partial Fulfillment for the Award of Degree of Bachelor of Technology in Information Technology from Rajasthan Technical University, Kota", cover_desc))

    attrib_table = [
        [
            Paragraph("<b>MENTOR:</b><br/>Faculty Mentor<br/>Dept. of Information Technology", body),
            Paragraph("<b>SUBMITTED BY:</b><br/><b>Member 4 (Lead Integrator &amp; UI)</b><br/>Roll No: 23ESKITXXX<br/><i>In collaboration with Members 1, 2 &amp; 3</i>", body)
        ],
        [
            Paragraph("<b>COORDINATOR:</b><br/>Project Coordinator<br/>Dept. of Information Technology", body),
            Paragraph("<b>PROJECT ID:</b> 2026-27-IT-G2<br/><b>SESSION:</b> 2026&ndash;27", body)
        ]
    ]
    t_attrib = Table(attrib_table, colWidths=[240, 260])
    t_attrib.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 14)]))
    story.append(t_attrib)
    story.append(Spacer(1, 35))

    inst_style = ParagraphStyle('InstStyle', parent=styles['Normal'], alignment=1, fontName='Helvetica-Bold', fontSize=8.5, leading=12, textColor=colors.HexColor('#0f172a'))
    story.append(Paragraph("DEPARTMENT OF INFORMATION TECHNOLOGY", inst_style))
    story.append(Paragraph("SWAMI KESHWANAND INSTITUTE OF TECHNOLOGY, MANAGEMENT &amp; GRAMOTHAN", inst_style))
    story.append(Paragraph("(An Autonomous Institute Affiliated to Rajasthan Technical University, Kota)", ParagraphStyle('Affil', parent=styles['Normal'], alignment=1, fontSize=7.5, leading=11, textColor=colors.HexColor('#475569'))))
    story.append(Paragraph("Ramnagaria (Jagatpura), Jaipur &ndash; 302017", ParagraphStyle('Addr', parent=styles['Normal'], alignment=1, fontSize=8, leading=11, textColor=colors.HexColor('#1e293b'))))
    story.append(Paragraph("<b>SESSION 2026&ndash;27</b>", ParagraphStyle('Sess', parent=inst_style, spaceBefore=3)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: REVISION HISTORY
    # =========================================================================
    story.append(Paragraph("Revision History", ParagraphStyle('RevHead', parent=h1_style, alignment=1, fontSize=13, spaceAfter=14)))
    rev_table = [
        [Paragraph("Date", th_style), Paragraph("Version", th_style), Paragraph("Description", th_style), Paragraph("Author", th_style)],
        [Paragraph("20/07/2026", td_style), Paragraph("0.1", td_style), Paragraph("Initial requirement analysis, 4-member pipeline formulation, and system scope.", td_style), Paragraph("Member 4", td_style)],
        [Paragraph("01/10/2026", td_style), Paragraph("1.0", td_style), Paragraph("Initial SRS draft with input/output contracts for Members 1, 2, and 3.", td_style), Paragraph("Member 4", td_style)],
        [Paragraph("31/10/2026", td_style), Paragraph("2.0", td_style), Paragraph("Revised SRS with complete Module 4 implementation (FastAPI backend, React Light UI, persistent results.csv storage, analytics suite, and test matrix).", td_style), Paragraph("Member 4", td_style)],
    ]
    t_rev = Table(rev_table, colWidths=[70, 45, 290, 95])
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
    # PAGE 3: TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("Table of Contents", ParagraphStyle('TOCHead', parent=h1_style, alignment=1, fontSize=13, spaceAfter=14)))
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
        ("    4.1 Client-Server Architecture", "9"),
        ("    4.2 Communications Interfaces", "9"),
        ("5  Design and Implementation", "10"),
        ("    5.1 Product Features & 4-Member Division", "10"),
        ("    5.2 Data Flow Diagrams (Level 0, 1 & 2)", "11"),
        ("    5.3 E-R Diagram", "14"),
        ("    5.4 Class Diagram Design", "14"),
        ("    5.5 Use Case Diagram", "15"),
        ("    5.6 Sequence Diagram", "18"),
        ("    5.7 Component Diagram", "19"),
        ("6  Conclusion and Future Scope", "20"),
        ("7  Mapping with UN Sustainable Development Goals", "21"),
    ]
    toc_data = []
    for t_str, p_str in toc_items:
        is_m = not t_str.startswith("    ")
        fn = 'Helvetica-Bold' if is_m else 'Helvetica'
        fs = 8.5 if is_m else 8.0
        cv = '#0f172a' if is_m else '#334155'
        toc_data.append([
            Paragraph(f"<font color='{cv}'>{t_str}</font>", ParagraphStyle('TOC_T', fontName=fn, fontSize=fs, leading=11)),
            Paragraph(f"<font color='{cv}'>{p_str}</font>", ParagraphStyle('TOC_P', fontName=fn, fontSize=fs, leading=11, alignment=2))
        ])
    t_toc = Table(toc_data, colWidths=[450, 50])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.6),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.HexColor('#f1f5f9')),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: 1 INTRODUCTION
    # =========================================================================
    story.append(Paragraph("1  Introduction", h1_style))
    story.append(Paragraph("1.1 Purpose", h2_style))
    story.append(Paragraph(
        "The purpose of this Software Requirements Specification (SRS) is to describe the technical architecture, "
        "functional requirements, and deployment specifications for the multi-modal facial emotion recognition suite named <b>FaceForge</b>. "
        "The system is a high-performance web-based application designed to detect human faces, isolate regions of interest (ROI), and classify affective expressions "
        "from three operating inputs: static photographs, video files, and real-time live browser webcam streams.<br/><br/>"
        "The application is structured into four distinct modules to facilitate collaborative development across four team members. "
        "This specification is authored by <b>Member 4</b> (Lead Integrator & UI Engineer) and provides complete operational specifications for the integration platform, "
        "while establishing standardized input/output interface contracts for Member 1 (Preprocessing), Member 2 (Computer Vision), and Member 3 (Emotion Model).",
        body
    ))
    story.append(Paragraph("1.2 Motivation", h2_style))
    story.append(Paragraph(
        "Facial expressions convey over 55% of human emotional communication. While machine learning research has yielded capable deep neural networks, "
        "practical real-world deployment is frequently hampered by high computational overhead, absent persistent telemetry, and clunky user interfaces.<br/><br/>"
        "FaceForge addresses these challenges by combining OpenCV frame-sampling optimization, a pretrained deep learning emotion model, an append-only telemetry storage ledger, "
        "and an accessible modern light-themed web interface. Rather than requiring users to configure complex Python environments, FaceForge provides an immediate, browser-accessible "
        "platform for facial expression analysis.",
        body
    ))
    story.append(Paragraph("1.3 Tools and Technologies", h2_style))
    story.append(Paragraph("The following tools and frameworks constitute the FaceForge platform:", body))
    story.append(Paragraph("&bull; <b>Frontend:</b> React 19, Vite, Vanilla CSS design tokens (Light theme), Lucide Icons.", bullet))
    story.append(Paragraph("&bull; <b>Backend:</b> Python 3.11, FastAPI, Uvicorn ASGI server, Starlette StaticFiles.", bullet))
    story.append(Paragraph("&bull; <b>Computer Vision:</b> OpenCV (cv2), NumPy array operations, Pillow (PIL).", bullet))
    story.append(Paragraph("&bull; <b>Machine Learning:</b> Pretrained FER Deep Learning Model (CNN), Softmax probabilities.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: 1.3 Tools cont. & 1.4 References
    # =========================================================================
    story.append(Paragraph("1.3 Tools and Technologies (Continued)", h2_style))
    story.append(Paragraph("&bull; <b>Storage &amp; Telemetry:</b> Append-only CSV storage engine (`storage.py` &rarr; `results/results.csv`), PyYAML.", bullet))
    story.append(Paragraph("&bull; <b>Analytics &amp; Visualization:</b> pandas, matplotlib, ReportLab PDF compilation.", bullet))
    story.append(Paragraph("&bull; <b>Development &amp; Version Control:</b> Visual Studio Code, Git, GitHub.", bullet))

    story.append(Spacer(1, 10))
    story.append(Paragraph("1.4 References", h2_style))
    story.append(Paragraph("1. Goodfellow, I., et al., <i>Challenges in Representation Learning: Facial Expression Recognition</i>, ICML, 2013.", bullet))
    story.append(Paragraph("2. OpenCV Open Source Computer Vision Library: https://opencv.org/", bullet))
    story.append(Paragraph("3. FastAPI Framework Documentation: https://fastapi.tiangolo.com/", bullet))
    story.append(Paragraph("4. React Documentation: https://react.dev/", bullet))
    story.append(Paragraph("5. Vite Documentation: https://vite.dev/guide/", bullet))
    story.append(Paragraph("6. Python 3 Documentation: https://docs.python.org/3/", bullet))
    story.append(Paragraph("7. Pandas Documentation: https://pandas.pydata.org/docs/", bullet))
    story.append(Paragraph("8. Matplotlib Documentation: https://matplotlib.org/stable/", bullet))
    story.append(Paragraph("9. IEEE Std 830-1998, <i>IEEE Recommended Practice for Software Requirements Specifications</i>.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: 2 MARKET SURVEY
    # =========================================================================
    story.append(Paragraph("2  Market Survey", h1_style))
    story.append(Paragraph("2.1 Objectives", h2_style))
    story.append(Paragraph(
        "The primary objectives of the market survey are: (1) To examine existing computer vision toolkits for facial analysis; "
        "(2) To study how video sampling step-rates mitigate frame-processing latency; (3) To identify usability limitations in current emotion detection systems; "
        "and (4) To compare FaceForge against conventional scripts and commercial cloud vision APIs.",
        body
    ))
    story.append(Paragraph("2.2 Unexplored Areas", h2_style))
    story.append(Paragraph(
        "Although emotion classification models are widely studied in research, several critical practical areas remain unaddressed in standard solutions: "
        "<br/>&bull; <b>Direct Multi-Modal Accessibility:</b> Most existing tools require separate scripts for static images, stored video files, and live webcams. "
        "FaceForge combines all three inputs into a unified user-friendly web interface."
        "<br/>&bull; <b>Persistent Telemetry Storage:</b> Standard vision demos only print classifications to terminal consoles without preserving structured historical records. "
        "FaceForge logs every prediction into an append-only CSV ledger."
        "<br/>&bull; <b>Aggregated Analytics:</b> Existing open-source scripts lack built-in statistical aggregation engines for class frequency, average confidence, and temporal valence changes."
        "<br/>&bull; <b>Decoupled Modular Architecture:</b> Monolithic scripts make collaborative engineering difficult. FaceForge establishes modular adapter contracts allowing team members to work independently.",
        body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: 2.3 Comparative Study (Table 2)
    # =========================================================================
    story.append(Paragraph("2.3 Comparative Study of Similar Solutions", h2_style))
    story.append(Paragraph("Table 2 compares the features and operational characteristics of standard open-source scripts and commercial solutions with FaceForge.", body))
    story.append(Spacer(1, 4))
    
    comp_data = [
        [Paragraph("Feature", th_style), Paragraph("Standard FER Scripts", th_style), Paragraph("Commercial Cloud APIs", th_style), Paragraph("FaceForge (Our System)", th_style)],
        [
            Paragraph("Primary Interface", td_style),
            Paragraph("CLI / Local OpenCV window", td_style),
            Paragraph("Proprietary Web Dashboard", td_style),
            Paragraph("Modern React Light Web UI (HMR)", td_style)
        ],
        [
            Paragraph("Multi-Modal Support", td_style),
            Paragraph("Single image or webcam only", td_style),
            Paragraph("Image / Cloud Video", td_style),
            Paragraph("Image, Video (Step Sampling), Webcam", td_style)
        ],
        [
            Paragraph("Data Privacy &amp; Hosting", td_style),
            Paragraph("Local machine only", td_style),
            Paragraph("Requires cloud upload", td_style),
            Paragraph("100% On-Premise / Local Host", td_style)
        ],
        [
            Paragraph("Telemetry Logging", td_style),
            Paragraph("Transient console output", td_style),
            Paragraph("Cloud database", td_style),
            Paragraph("Persistent results.csv ledger", td_style)
        ],
        [
            Paragraph("Analytics Visualizer", td_style),
            Paragraph("None", td_style),
            Paragraph("Built-in dashboards", td_style),
            Paragraph("Dynamic charts &amp; PDF reports", td_style)
        ],
        [
            Paragraph("Collaborative Structure", td_style),
            Paragraph("Monolithic script", td_style),
            Paragraph("Proprietary closed-source", td_style),
            Paragraph("4-Module Decoupled Architecture", td_style)
        ]
    ]
    t_comp = Table(comp_data, colWidths=[95, 120, 125, 160])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#334155')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Table 2:</b> Comparison of Standard Solutions, Commercial Systems, and FaceForge", caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: 3 REQUIREMENTS (FR & NFR)
    # =========================================================================
    story.append(Paragraph("3  Requirements", h1_style))
    story.append(Paragraph("3.1 Functional Requirements", h2_style))
    story.append(Paragraph("&bull; <b>Image Emotion Detection:</b> The system shall accept JPG and PNG image uploads, detect face coordinates, draw bounding box overlays, and report the dominant emotion and confidence.", bullet))
    story.append(Paragraph("&bull; <b>Video Frame Sampling:</b> The system shall process MP4 and AVI video files by sampling every N-th frame (configurable 1-30) to balance processing throughput and detection fidelity.", bullet))
    story.append(Paragraph("&bull; <b>Real-Time Webcam Streaming:</b> The system shall connect to client browser webcams, process sequential video frames, and render a live floating HUD with active affective state and confidence percentage.", bullet))
    story.append(Paragraph("&bull; <b>Telemetry Storage Ledger:</b> All detections across all three modes shall be automatically recorded in `results/results.csv` with timestamp, source, frame number, face ID, emotion, and confidence.", bullet))
    story.append(Paragraph("&bull; <b>Historical Ledger Querying:</b> The system shall allow filtering recorded telemetry by source medium, emotion category, and data tier (live vs demo).", bullet))
    story.append(Paragraph("&bull; <b>Analytics Engine:</b> The system shall calculate frequency distributions across the 7 canonical emotions, average confidence, and temporal emotion timelines.", bullet))
    story.append(Paragraph("&bull; <b>Configuration Management:</b> The system shall provide feature toggles in `config.yaml` to enable or bypass teammate modules independently using non-crashing mock adapters.", bullet))

    story.append(Paragraph("3.2 Non-Functional Requirements", h2_style))
    story.append(Paragraph("&bull; <b>Performance &amp; Latency:</b> Static image analysis shall return inference responses within 800 ms. Video processing with sampling step 10 shall maintain equivalent throughput of > 20 FPS.", bullet))
    story.append(Paragraph("&bull; <b>Usability &amp; Design:</b> The interface shall adhere to a clean light theme with WCAG AA compliant contrast, clear iconography, and responsive layout.", bullet))
    story.append(Paragraph("&bull; <b>Reliability &amp; Fault Tolerance:</b> Uploads without faces or corrupted media files shall trigger graceful user notices without crashing the backend service.", bullet))
    story.append(Paragraph("&bull; <b>Data Integrity:</b> The storage engine shall enforce atomic append operations to preserve telemetry records against simultaneous write collisions.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: 3.2 NFR cont., 3.3 Hardware & 3.4 Software
    # =========================================================================
    story.append(Paragraph("3.2 Non-Functional Requirements (Continued)", h2_style))
    story.append(Paragraph("&bull; <b>Compatibility:</b> The system shall be accessible across modern web browsers (Chrome, Edge, Firefox, Safari) on desktop and laptop devices.", bullet))
    story.append(Paragraph("&bull; <b>Security &amp; Privacy:</b> Visual media and webcam frames shall be processed locally on-premise without external third-party data transfers.", bullet))

    story.append(Spacer(1, 8))
    story.append(Paragraph("3.3 Hardware Requirements", h2_style))
    story.append(Paragraph("&bull; <b>Host / Development Computer:</b> Desktop or laptop with dual-core Intel Core i3 / AMD Ryzen 3 or higher, minimum 4 GB RAM, and 2 GB free storage space.", bullet))
    story.append(Paragraph("&bull; <b>Video Capture Device:</b> Integrated HD camera or USB webcam supporting standard 720p resolution at 30 FPS.", bullet))
    story.append(Paragraph("&bull; <b>Display Resolution:</b> Minimum 1280 &times; 720 display resolution for optimal UI rendering.", bullet))

    story.append(Spacer(1, 8))
    story.append(Paragraph("3.4 Software Requirements", h2_style))
    story.append(Paragraph("&bull; <b>Operating System:</b> Windows 10/11, Ubuntu 20.04+, or macOS.", bullet))
    story.append(Paragraph("&bull; <b>Programming Languages:</b> Python 3.10+, JavaScript (ES6+), HTML5, and CSS3.", bullet))
    story.append(Paragraph("&bull; <b>Frontend Stack:</b> React 19, Vite bundler, Lucide Icons.", bullet))
    story.append(Paragraph("&bull; <b>Backend Stack:</b> FastAPI, Uvicorn ASGI server, Starlette StaticFiles.", bullet))
    story.append(Paragraph("&bull; <b>Computer Vision &amp; ML:</b> OpenCV-Python, NumPy, Pillow, FER library.", bullet))
    story.append(Paragraph("&bull; <b>Storage &amp; Analytics:</b> Pandas, Matplotlib, ReportLab, PyYAML.", bullet))
    story.append(Paragraph("&bull; <b>Development Environment:</b> Visual Studio Code, Git, GitHub.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: 3.5 Agile Model (Figure 1) & 3.6 Business Process
    # =========================================================================
    story.append(Paragraph("3.5 Agile Model", h2_style))
    story.append(Paragraph(
        "The Agile development model was adopted for FaceForge, structuring engineering into iterative sprints. "
        "Tasks were divided into manageable stages: requirement analysis, mock adapter construction, API gateway development, "
        "React Light UI integration, and analytics verification. Figure 1 illustrates the iterative lifecycle followed.",
        body
    ))
    story.append(Spacer(1, 4))
    story.append(load_img("fig1_agile.png", w=260, h=190))
    story.append(Paragraph("<b>Figure 1:</b> Agile Development Model Followed in FaceForge", caption))

    story.append(Paragraph("3.6 Business Process Model", h2_style))
    story.append(Paragraph("The operational workflow of FaceForge begins when an analyst opens the web portal:", body))
    story.append(Paragraph("1. User selects desired mode (Image, Video, or Live Webcam).", bullet))
    story.append(Paragraph("2. System acquires visual data via file upload or browser camera stream.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: 3.6 Business Process cont. & 3.7 Supplementary
    # =========================================================================
    story.append(Paragraph("3.6 Business Process Model (Continued)", h2_style))
    story.append(Paragraph("3. Preprocessing converts matrix to normalized format.", bullet))
    story.append(Paragraph("4. Face detector locates faces and outputs coordinates (x, y, w, h).", bullet))
    story.append(Paragraph("5. Extracted face ROI is fed to the pretrained FER model.", bullet))
    story.append(Paragraph("6. Dominant emotion and confidence scores are determined.", bullet))
    story.append(Paragraph("7. Inference record is appended atomically to results.csv.", bullet))
    story.append(Paragraph("8. Visual bounding overlays, tables, and analytics charts update dynamically.", bullet))

    story.append(Spacer(1, 10))
    story.append(Paragraph("3.7 Supplementary Requirements", h2_style))
    story.append(Paragraph("&bull; <b>Camera Permissions:</b> Live webcam streaming requires user browser permission for camera access.", bullet))
    story.append(Paragraph("&bull; <b>Graceful Fallbacks:</b> In the absence of teammate modules (M1, M2, M3), built-in adapters provide mock responses so that UI and storage testing proceed without interruption.", bullet))
    story.append(Paragraph("&bull; <b>System Boundary:</b> FaceForge operates as an analytical and diagnostic tool and does not connect to external surveillance networks.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: 4 SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("4  System Architecture", h1_style))
    story.append(Paragraph("4.1 Client-Server Architecture", h2_style))
    story.append(Paragraph(
        "FaceForge follows a client-server architecture consisting of a React Single-Page Application (SPA) frontend, "
        "a FastAPI backend application server, a persistent file-based CSV telemetry store, and modular adapter pipelines.<br/><br/>"
        "The frontend is built using React 19 and Vite. It provides modern interfaces for image uploads, video frame sampling, "
        "webcam feeds, results exploration, and analytics reporting.<br/><br/>"
        "The backend is developed with FastAPI and Python. It handles REST requests, routes inputs through the modular adapters, "
        "annotates images with bounding boxes, writes to `results.csv`, and serves static assets. Figure 2 illustrates the overall architecture.",
        body
    ))
    story.append(Paragraph("4.2 Communications Interfaces", h2_style))
    story.append(Paragraph("&bull; <b>Client-Server REST APIs:</b> HTTP/1.1 JSON communication between React and FastAPI on port 8000.", bullet))
    story.append(Paragraph("&bull; <b>Multipart File Protocol:</b> Standard form-data encoding for image and video uploads.", bullet))
    story.append(Paragraph("&bull; <b>Webcam Frame Protocol:</b> Base64 image payload posting for real-time webcam analysis.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: Figure 2 & 5 Design and Implementation
    # =========================================================================
    story.append(load_img("fig2_system_architecture.png", w=450, h=230))
    story.append(Paragraph("<b>Figure 2:</b> System Architecture of FaceForge", caption))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5  Design and Implementation", h1_style))
    story.append(Paragraph("5.1 Product Features & 4-Member Collaborative Division", h2_style))
    story.append(Paragraph(
        "To ensure modularity, the system is partitioned into four independent components across the four team members. "
        "Members 1, 2, and 3 are provided standardized input/output interfaces, while Member 4 delivers the complete web application, "
        "API gateway, telemetry storage, and analytics.",
        body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 14: 5.1 Stubs & DFD Level 0 (Figure 3)
    # =========================================================================
    # M1, M2, M3 Stubs
    m_stubs = [
        [Paragraph("<b>[MODULE 1: DATASET &amp; PREPROCESSING &mdash; MEMBER 1]</b><br/>Input: Raw images/FER-2013 &bull; Output: Normalized grayscale matrix &bull; <i>To be documented by Member 1.</i>", stub_box)],
        [Paragraph("<b>[MODULE 2: COMPUTER VISION &amp; FACE DETECTION &mdash; MEMBER 2]</b><br/>Input: Image matrix &bull; Output: Bounding coordinates (x,y,w,h) &amp; cropped ROI &bull; <i>To be documented by Member 2.</i>", stub_box)],
        [Paragraph("<b>[MODULE 3: PRETRAINED MODEL &amp; EVALUATION &mdash; MEMBER 3]</b><br/>Input: Face ROI &bull; Output: 7-class emotion probabilities &amp; F1/Confusion Matrix &bull; <i>To be documented by Member 3.</i>", stub_box)],
        [Paragraph("<b>[MODULE 4: INTEGRATION, UI, STORAGE &amp; ANALYTICS &mdash; MEMBER 4 (ACTIVE)]</b><br/>Input: Multi-modal streams &bull; Output: Live React UI, REST APIs, results.csv ledger &bull; <i>100% Fully Built.</i>", active_box)],
    ]
    t_stubs = Table(m_stubs, colWidths=[500])
    t_stubs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,2), colors.HexColor('#fffbeb')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#ecfdf5')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_stubs)
    story.append(Spacer(1, 8))

    story.append(Paragraph("5.2 Data Flow Diagrams (DFDs)", h2_style))
    story.append(Paragraph("DFD Level 0 (Context Diagram)", h3_style))
    story.append(load_img("fig3_dfd_level0.png", w=440, h=190))
    story.append(Paragraph("<b>Figure 3:</b> FaceForge Data Flow Diagram &ndash; Level 0", caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 15: DFD Level 1 (Figure 4)
    # =========================================================================
    story.append(Paragraph("DFD Level 1", h2_style))
    story.append(Paragraph(
        "The Level 1 DFD illustrates the major processes of FaceForge: Media Acquisition (1.0), Preprocessing (2.0), "
        "Face Detection (3.0), Emotion Inference (4.0), and Telemetry Storage & Analytics (5.0).",
        body
    ))
    story.append(Spacer(1, 6))
    story.append(load_img("fig4_dfd_level1.png", w=450, h=230))
    story.append(Paragraph("<b>Figure 4:</b> FaceForge Data Flow Diagram &ndash; Level 1", caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 16: DFD Level 2 (Figure 5)
    # =========================================================================
    story.append(Paragraph("DFD Level 2", h2_style))
    story.append(Paragraph(
        "The Level 2 DFD decomposes Module 4's processing pipeline: Route Dispatching, Pipeline Coordination with Adapters, "
        "Response Formatting, Telemetry Logging (`storage.py`), and Analytics Aggregation (`analytics.py`).",
        body
    ))
    story.append(Spacer(1, 6))
    story.append(load_img("fig5_dfd_level2.png", w=450, h=230))
    story.append(Paragraph("<b>Figure 5:</b> FaceForge Data Flow Diagram &ndash; Level 2", caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 17: 5.3 E-R Diagram (Figure 6) & 5.4 Class Diagram
    # =========================================================================
    story.append(Paragraph("5.3 E-R Diagram", h2_style))
    story.append(Paragraph(
        "The Entity-Relationship (E-R) diagram represents the data structure of FaceForge and the schema of `results.csv`, "
        "system configuration flags in `config.yaml`, and the analytical summary vectors.",
        body
    ))
    story.append(Spacer(1, 4))
    story.append(load_img("fig6_er_diagram.png", w=440, h=210))
    story.append(Paragraph("<b>Figure 6:</b> FaceForge Entity-Relationship &amp; Telemetry Schema Diagram", caption))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5.4 Class Diagram Design", h2_style))
    story.append(Paragraph(
        "The class diagram presents the main modules of FaceForge, their attributes, methods, and relationships. "
        "It illustrates the interactions between `controller.py`, `storage.py`, `analytics.py`, and the teammate adapters.",
        body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 18: Figure 7 & 5.5 Use Case Diagram
    # =========================================================================
    story.append(load_img("fig7_class_diagram.png", w=450, h=230))
    story.append(Paragraph("<b>Figure 7:</b> FaceForge UML Class Diagram", caption))
    story.append(Spacer(1, 4))

    story.append(Paragraph("5.5 Use Case Diagram", h2_style))
    story.append(Paragraph(
        "The use case diagrams describe how analysts and users interact with FaceForge across all modes: "
        "uploading images, analyzing videos, streaming live webcams, filtering results, and viewing analytics.",
        body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 19: Figure 8: Use Cases
    # =========================================================================
    story.append(Paragraph("User and Analyst Use Cases", h2_style))
    story.append(Spacer(1, 4))
    story.append(load_img("fig8_use_case_main.png", w=440, h=260))
    story.append(Paragraph("<b>Figure 8:</b> FaceForge User and Analyst Use Cases", caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 20: Figure 9: Video Frame & Telemetry Use Cases
    # =========================================================================
    story.append(Paragraph("Video Frame Sampling & Telemetry Use Cases", h2_style))
    story.append(Spacer(1, 4))
    story.append(load_img("fig9_use_case_telemetry.png", w=440, h=240))
    story.append(Paragraph("<b>Figure 9:</b> FaceForge Video Frame Sampling &amp; Telemetry Use Cases", caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 21: 5.6 Sequence Diagram (Figure 10)
    # =========================================================================
    story.append(Paragraph("5.6 Sequence Diagram", h2_style))
    story.append(Paragraph(
        "The sequence diagram illustrates the workflow of a detection request: from file selection on the React frontend "
        "to FastAPI route dispatch, controller execution, adapter inference, telemetry persistence, and UI overlay rendering.",
        body
    ))
    story.append(Spacer(1, 4))
    story.append(load_img("fig10_sequence_diagram.png", w=450, h=260))
    story.append(Paragraph("<b>Figure 10:</b> FaceForge Detection Pipeline Sequence Diagram", caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 22: 5.7 Component Diagram (Figure 11)
    # =========================================================================
    story.append(Paragraph("5.7 Component Diagram", h2_style))
    story.append(Paragraph(
        "The component diagram illustrates the software architecture of FaceForge, showing the React SPA frontend, "
        "FastAPI application server, pipeline coordinator, telemetry storage engine, and modular adapters.",
        body
    ))
    story.append(Spacer(1, 4))
    story.append(load_img("fig11_component_diagram.png", w=450, h=240))
    story.append(Paragraph("<b>Figure 11:</b> FaceForge UML Component Diagram", caption))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 23: 6 CONCLUSION AND FUTURE SCOPE
    # =========================================================================
    story.append(Paragraph("6  Conclusion and Future Scope", h1_style))
    story.append(Paragraph("Conclusion", h2_style))
    story.append(Paragraph(
        "FaceForge is an accessible, multi-modal facial emotion recognition suite engineered to analyze static images, video files, and real-time live webcams. "
        "By packaging an established pretrained deep learning model within an optimized computer vision pipeline, persistent CSV storage ledger, and a modern light-themed "
        "web interface, the system achieves robust real-time performance on standard desktop hardware.<br/><br/>"
        "The project demonstrates a successful collaborative architecture where Member 4 provides the operational web application, persistent storage, and analytical dashboards, "
        "while providing standardized interfaces for Members 1, 2, and 3 to contribute their preprocessing routines, detection algorithms, and evaluation benchmarks.",
        body
    ))
    story.append(Paragraph("Future Scope", h2_style))
    story.append(Paragraph("The following enhancements may be considered in future releases:", body))
    story.append(Paragraph("&bull; <b>Custom Model Fine-Tuning:</b> Retraining on domain-specific emotional datasets to capture nuanced cultural expressions.", bullet))
    story.append(Paragraph("&bull; <b>GPU CUDA Acceleration:</b> Utilizing NVIDIA CUDA acceleration for processing ultra-high-definition multi-face video streams at 60 FPS.", bullet))
    story.append(Paragraph("&bull; <b>Mobile Application:</b> Packaging the React client into a Progressive Web App (PWA) or Flutter mobile application.", bullet))
    story.append(Paragraph("&bull; <b>Advanced Longitudinal Analytics:</b> Integrating longitudinal affective wellness tracking for educational and clinical environments.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 24: 7 MAPPING WITH UN SDGS
    # =========================================================================
    story.append(Paragraph("7  Mapping with UN Sustainable Development Goals", h1_style))
    story.append(Paragraph("The following table describes the relevance of FaceForge to selected United Nations Sustainable Development Goals (SDGs):", body))
    story.append(Spacer(1, 6))

    sdg_table = [
        [Paragraph("SDG No.", th_style), Paragraph("SDG Title", th_style), Paragraph("Relevance to FaceForge Project", th_style)],
        [
            Paragraph("<b>SDG 3</b>", td_style),
            Paragraph("Good Health and Well-being", td_style),
            Paragraph("Facial expression monitoring can provide non-invasive mental health screening, stress detection, and patient affective state tracking in telehealth.", td_style)
        ],
        [
            Paragraph("<b>SDG 4</b>", td_style),
            Paragraph("Quality Education", td_style),
            Paragraph("Enables automated learner engagement analysis in classrooms and e-learning platforms, helping educators identify student confusion or fatigue.", td_style)
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
    t_sdg = Table(sdg_table, colWidths=[65, 135, 300])
    t_sdg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#334155')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_sdg)

    # Build PDF
    doc.build(story, canvasmaker=ExactTeamBCanvas)
    print(f"Built local PDF: {LOCAL_PDF_PATH}")

    # Copy to Desktop
    import shutil
    shutil.copyfile(LOCAL_PDF_PATH, DESKTOP_PDF_PATH)
    print(f"Copied final PDF directly to Desktop: {DESKTOP_PDF_PATH}")

if __name__ == "__main__":
    build_exact_pdf()

