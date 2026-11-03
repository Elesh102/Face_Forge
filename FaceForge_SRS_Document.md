# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## FaceForge: Multi-Modal Facial Emotion Recognition System
### Final Year Project — 4-Member Collaborative Implementation

---

## Document Control & Team Attribution

| Role | Member | Responsibilities | Status in SRS |
| :--- | :--- | :--- | :--- |
| **Member 1** | Data & Preprocessing Specialist | FER-2013 dataset collection, cleaning, grayscale conversion, normalization, and test set partitioning | **Template Stub** *(To be completed by Member 1)* |
| **Member 2** | Computer Vision & Detection Engineer | OpenCV camera input, face localization `(x, y, w, h)`, face ROI extraction, and video frame extraction | **Template Stub** *(To be completed by Member 2)* |
| **Member 3** | Pretrained Model & Evaluation Specialist | FER library integration, 7 emotion probabilities, confusion matrix heatmap, F1 score, and error analysis | **Template Stub** *(To be completed by Member 3)* |
| **Member 4** | **System Integration, UI, Storage & Analytics** | **Full application orchestrator (`app.py`), Web UI (Image, Video, Webcam), append-only telemetry storage (`results.csv`), and analytics engine** | **100% Fully Specified & Built** *(Active Module)* |

---

# 1. Project Overview & Objective

### 1.1 Objective
The primary objective of **FaceForge** is to engineer a multi-modal, real-time facial expression analysis application capable of detecting human faces, isolating regions of interest (ROI), and classifying emotional valence from three distinct visual input sources:
1. **Static Image Mode**: High-resolution JPG and PNG photographs.
2. **Video Clip Mode**: Stored MP4 and AVI files with adaptive frame-step sampling to minimize CPU load.
3. **Live Webcam Stream**: Continuous browser camera input via `getUserMedia` / OpenCV capture for real-time inference.

### 1.2 Core Architectural Principle
As established in the system roadmap:
> *"The project does not require training a deep learning network from scratch. Instead, it engineers an enterprise-grade multi-modal vision pipeline around an established pretrained FER neural network, backed by rigorous evaluation, persistent telemetry storage, and an interactive analytical dashboard."*

---

# 2. Complete System Pipeline & Four-Layer Architecture

```
                          ┌────────────────────────┐
                          │   USER INPUT CHOICE    │
                          └───────────┬────────────┘
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
          ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
          │ STATIC IMAGE│      │ VIDEO FILE  │      │ LIVE WEBCAM │
          └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
                 │                    │ (Frame Sampling)   │
                 └────────────────────┼────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ LAYER 1: DATA ACQUISITION │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ LAYER 2: COMPUTER VISION  │
                        │ - Image Preprocessing     │
                        │ - Face Detection (x,y,w,h)│
                        │ - ROI Face Extraction     │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ LAYER 3: EMOTION AI       │
                        │ - Pretrained FER Model    │
                        │ - 7 Emotion Probabilities │
                        │ - Dominant Class Argmax   │
                        └─────────────┬─────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ LAYER 4: INTEGRATION & UI │
                        │ - Visual Bounding Boxes   │
                        │ - Storage Engine (CSV)    │
                        │ - Analytics & Visualizer  │
                        └───────────────────────────┘
```

### Layer Breakdown
- **Layer 1: Input & Data Acquisition Layer**: Interfaces with client uploads and camera hardware.
- **Layer 2: Computer Vision Layer**: Handles image matrix decoding, resizing, grayscale conversions, face bounding box coordinates, and cropping the facial sub-matrix.
- **Layer 3: AI & Emotion Detection Layer**: Passes the cropped face into the pretrained model and generates probability distributions across 7 canonical expressions: `happy`, `sad`, `neutral`, `surprise`, `angry`, `fear`, and `disgust`.
- **Layer 4: Output, Storage & Analytics Layer (Member 4)**: Renders bounding boxes and confidence pills, logs append-only inference telemetry, and generates statistical charts.

---

# 3. Module Specifications & Responsibilities

---

## 🔹 SECTION A: MEMBER 1 — DATASET & PREPROCESSING SPECIFICATIONS
*(Template Stub — Content to be populated by Member 1)*

### 3.1 Data Acquisition & Storage Organization
- **Dataset Identification**: FER-2013 (Facial Expression Recognition 2013 Dataset from Kaggle).
- **Directory Structure**:
  ```text
  dataset/
  ├── train/
  ├── test/
  └── validation/
  ```
- **Task Description**: `[To be documented by Member 1: Detailed class count, raw image dimensions (48x48), grayscale depth, and label encoding].`

### 3.2 Image Preprocessing Pipeline
- **Functions Defined**:
  - `resize_image(img, target_dim)`
  - `convert_to_grayscale(img)`
  - `normalize_pixel_values(img)`
- **Detailed Algorithms**: `[To be documented by Member 1: Specific color-space conversion routines, histogram equalization details, and tensor normalization formulas].`

### 3.3 Test Dataset Partitioning
- **Task Description**: `[To be documented by Member 1: Partitioning methodology for validation subsets across all 7 emotions to support Member 3's evaluation].`

---

## 🔹 SECTION B: MEMBER 2 — COMPUTER VISION & DETECTION SPECIFICATIONS
*(Template Stub — Content to be populated by Member 2)*

### 3.4 Face Detection & Bounding Box Localization
- **Coordinate Schema**: Rectangular tuple $(x, y, w, h)$.
- **Detector Implementation**: OpenCV Haar Cascade / selected deep learning face detector.
- **Task Description**: `[To be documented by Member 2: Min/max face size parameters, scaleFactor, minNeighbors, and multi-face array handling].`

### 3.5 Region of Interest (ROI) Face Extraction
- **Matrix Slicing Equation**: `face_roi = image[y:y+h, x:x+w]`
- **Task Description**: `[To be documented by Member 2: Boundary clipping guardrails, aspect-ratio preservation, and multiple simultaneous face cropping].`

### 3.6 Video & Webcam Stream Frame Extraction
- **Sampling Logic**: `if frame_count % video_sampling_step == 0:`
- **Task Description**: `[To be documented by Member 2: cv2.VideoCapture mechanics, buffer flushing, timestamp extraction, and webcam fps stabilization].`

---

## 🔹 SECTION C: MEMBER 3 — PRETRAINED MODEL & EVALUATION SPECIFICATIONS
*(Template Stub — Content to be populated by Member 3)*

### 3.7 Pretrained FER Model Integration
- **Model Framework**: Pretrained Deep Learning CNN (FER library).
- **Input Specifications**: Single-face cropped image tensor.
- **Output Schema**: 7-class probability vector:
  $$\sum_{i=1}^{7} P(\text{emotion}_i) = 1.0$$
- **Dominant Emotion Resolution**: $\text{dominant} = \arg\max_i P(\text{emotion}_i)$.
- **Task Description**: `[To be documented by Member 3: Underlying architecture layers, weight origins, inference latency per face, and memory footprint].`

### 3.8 Model Evaluation & Error Analysis
- **Deliverables**:
  - `metrics_report.txt` (Precision, Recall, F1-Score per emotion category).
  - `confusion_matrix.png` (7x7 heatmap illustrating inter-class confusion).
  - `error_analysis.md` (Systematic review of lighting dependencies, head pose tilt, and occlusion failures).
- **Task Description**: `[To be documented by Member 3: Benchmark results against the evaluation dataset prepared by Member 1].`

---

## 🔹 SECTION D: MEMBER 4 — SYSTEM INTEGRATION, UI, STORAGE & ANALYTICS SPECIFICATIONS
*(Fully Implemented — Module 4 Deliverables)*

### 3.9 Main Application Architecture (`app.py` & `controller.py`)
Member 4 serves as the system integrator, uniting all three upstream components into a non-crashing service with hot-swappable mock adapters and configuration toggles.

```
+------------------------------------------------------------------------+
|               MODULE 4: INTEGRATION & PIPELINE ORCHESTRATOR            |
|                                                                        |
|  [config.yaml] <---> [controller.py] <---> [storage.py] (results.csv)  |
|         │                     │                         │              |
|         ▼                     ▼                         ▼              |
|  Feature Toggles     Adapter Dispatcher           Append Ledger        |
|  - demo_mode         - adapter_preprocess (M1)                         |
|  - use_module1       - adapter_face (M2)                               |
|  - use_module2       - adapter_emotion (M3)                            |
|  - confidence_thr             │                                        |
|  - sampling_step              ▼                                        |
|                       REST API GATEWAY                                 |
|                       - /api/detect/image                              |
|                       - /api/detect/video                              |
|                       - /api/detect/webcam-frame                       |
|                       - /api/results                                   |
|                       - /api/analytics                                 |
|                       - /api/config                                    |
+------------------------------------------------------------------------+
```

### 3.10 Web User Interface Specifications
The frontend is constructed using modern responsive component architecture featuring a light color palette (Slate 900 typography `#0f172a`, Electric Indigo accents `#4f46e5`, Emerald status indicators `#059669`, and clean cards `#ffffff`).

1. **Home Screen (`HomeView.jsx`)**:
   - High-level system overview with direct launch action cards.
   - Quick telemetry counters displaying total recorded inferences and system readiness.
2. **Static Image Detection Screen (`ImageView.jsx`)**:
   - Drag-and-drop file upload zone supporting JPG, JPEG, and PNG.
   - Dual-panel layout displaying preview with annotated bounding box overlays and tabular predictions.
3. **Video Detection Screen (`VideoView.jsx`)**:
   - HTML5 video player and file selector for MP4 and AVI files.
   - Interactive slider control for configuring frame sampling steps ($N \in [1, 30]$).
   - Real-time progress bar indicator during frame extraction.
4. **Live Webcam Screen (`WebcamView.jsx`)**:
   - Browser camera stream integration via `navigator.mediaDevices.getUserMedia`.
   - Start / Stop streaming controls.
   - Floating glassmorphism HUD displaying dominant emotion and live confidence percentage.
5. **Results Ledger Screen (`ResultsView.jsx`)**:
   - Searchable, filterable table indexing historical records from `results.csv`.
   - Multi-criteria filter dropouts: by source (`image`, `video`, `webcam`), emotion category, and data tier (`live` vs `demo`).
   - Direct CSV download export button.
   - Safe reset confirmation dialog to prevent accidental data loss.
6. **Analytics Dashboard (`AnalyticsView.jsx`)**:
   - Bar chart visualizing frequency distribution across all 7 emotions.
   - Average confidence score tracker.
   - Timeline distribution and valence insights.
   - One-click PDF report generation.
7. **System Configuration Screen (`SettingsView.jsx`)**:
   - UI toggles to enable or bypass teammate modules independently.
   - Global confidence threshold adjustment.
   - Video sampling rate modifier.

### 3.11 Telemetry Storage Engine (`storage.py`)
All model inferences are recorded into an append-only persistent CSV ledger:
- **Location**: `results/results.csv`
- **Schema Specification**:

| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `timestamp` | `String (YYYY-MM-DD HH:MM:SS)` | UTC/local system timestamp | `2026-10-31 19:39:24` |
| `source` | `String (Enum)` | Input medium | `image`, `video`, `webcam` |
| `file_name` | `String` | Source file name or camera tag | `sample_face.jpg` |
| `frame_number` | `Integer` | Video/stream frame index | `140` (or `0` for image) |
| `face_id` | `Integer` | Zero-indexed detected face index | `0` |
| `emotion` | `String` | Dominant emotion label | `Happy` |
| `confidence` | `Float` | Model confidence probability $[0.0, 1.0]$ | `0.92` |
| `status` | `String` | Human-readable affective category | `Happy`, `Neutral`, `Needs attention` |
| `data_source` | `String` | Data provenance flag | `live` or `demo` |

### 3.12 Statistical Analytics Engine (`analytics.py`)
Aggregates the telemetry ledger to produce real-time metrics:
- **Frequency Distribution**: Computes absolute and percentage counts for each of the 7 classes.
- **Mean Confidence Metric**: Evaluates average model certainty across all processed faces.
- **Temporal Analysis**: Tracks emotional fluctuations across sequential video frames.

---

# 4. Master Testing & Verification Matrix

| Test ID | Phase | Test Description | Expected Behavior | Responsible Member |
| :--- | :--- | :--- | :--- | :--- |
| **T1** | Image | Clear happy portrait (JPG) | Bounding box placed, emotion tagged `Happy`, confidence $> 75\%$ | Member 4 + M2/M3 |
| **T2** | Image | Sad portrait | Emotion tagged `Sad`, stored in `results.csv` | Member 4 + M2/M3 |
| **T3** | Image | Angry expression | Emotion tagged `Angry`, confidence reported accurately | Member 4 + M2/M3 |
| **T4** | Image | Neutral expression | Emotion tagged `Neutral` | Member 4 + M2/M3 |
| **T5** | Image | Multi-person group photo | Multiple distinct bounding boxes detected and logged | Member 2 + M4 |
| **T6** | Image | Landscape with no faces | System reports 0 faces detected without throwing 500 error | Member 2 + M4 |
| **T7** | Image | Low illumination portrait | Fallback/warning triggered if confidence falls below threshold | Member 1 + M4 |
| **T8** | Video | Short 10-second MP4 | Frames sampled every $N$ steps, progress bar rendered | Member 2 + M4 |
| **T9** | Video | Multiple people in frame | Separate face telemetry recorded for each frame interval | Member 2 + M4 |
| **T10** | Video | Subject changing emotions | Emotion timeline graph in Analytics reflects transitions | Member 3 + M4 |
| **T11** | Video | Low-spec machine (i3/4GB) | Frame sampling avoids CPU freeze; smooth completion | Member 4 |
| **T12** | Webcam | Standard daylight lighting | Real-time face tracking with live confidence pill updates | Member 2 + M4 |
| **T13** | Webcam | Dim ambient room | Robust detection without browser camera disconnect | Member 1 + M4 |
| **T14** | Webcam | Rapid face turning / side pose | Graceful handling when face leaves camera field of view | Member 2 + M4 |
| **T15** | System | Storage reset action | `results.csv` cleared safely after user confirmation modal | Member 4 |

---

# 5. System Limitations & Future Scope

### 5.1 Known Limitations
1. **Hardware Sensitivity**: High frame-rate video analysis on dual-core/i3 processors requires frame sampling steps $\ge 10$ to prevent lag.
2. **Lighting Dependencies**: Extreme backlighting or deep shadows can degrade face detection accuracy.
3. **Subtle Micro-Expressions**: Fleeting facial micro-expressions $(< 200\text{ms})$ may be skipped during video frame sampling.

### 5.2 Future Scope
1. **Custom Model Fine-Tuning**: Retraining the model with domain-specific emotional datasets.
2. **GPU Acceleration**: CUDA integration for processing ultra-high-definition multi-face feeds at 60 FPS.
3. **Longitudinal Affective Tracking**: Patient mental wellness and classroom engagement analytics.

---

# 6. Conclusion
The FaceForge system successfully unifies data preprocessing (Module 1), face localization (Module 2), deep emotion classification (Module 3), and full-stack integration (Module 4) into an enterprise-grade, accessible web suite. Through graceful fallback adapters and modular design, each teammate's individual contribution can be developed, tested, and integrated independently without disrupting the functional system.
