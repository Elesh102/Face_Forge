# FaceForge: Multi-Modal Facial Emotion Recognition System

**FaceForge** is an end-to-end Computer Vision and Deep Learning system designed to detect human faces and classify facial emotional expressions in real time across **still images**, **pre-recorded videos**, and **live webcams**.

---

## 👥 Project Team & Modular Architecture

The project is structured into four decoupled, adapter-integrated modules:

| Module | Member Responsibility | Core Files | Description |
| :--- | :--- | :--- | :--- |
| **Module 1** | **Dataset & Preprocessing** | `module1_preprocess.py`, `adapter_preprocess.py` | FER-2013 data pipeline, CLAHE lighting contrast enhancement, $(48 \times 48 \times 1)$ tensor formatting. |
| **Module 2** | **Computer Vision & Face Detection** | `module2_detection.py`, `adapter_face.py`, `models/` | OpenCV Haar Cascade (Frontal + Profile multi-angle detection), safe `float32`/`uint8` handling, texture false-positive rejection. |
| **Module 3** | **Emotion Classification Model** | `module3_model.py`, `adapter_emotion.py`, `emotion_model.onnx` | 4-Block Deep CNN with OpenCV DNN inference engine classifying 7 canonical emotions with softmax probability distributions. |
| **Module 4** | **System Integration, UI, Storage & Analytics** | `app.py`, `controller.py`, `storage.py`, `analytics.py`, `frontend/` | FastAPI REST gateway, React single-page dashboard, append-only CSV persistence with formula injection defense, Admin PIN protection. |

---

## 🎯 Canonical Emotions (FER-2013)

The system classifies faces into the 7 canonical emotion classes standardized on the FER-2013 dataset:
1. `0: Angry`
2. `1: Disgust`
3. `2: Fear`
4. `3: Happy`
5. `4: Sad`
6. `5: Surprise`
7. `6: Neutral`

---

## 📊 Model Architecture & Ground Truth Benchmark

- **Model Framework:** Deep Facial Expression Recognition (`fer` with TFLite / OpenCV DNN backend)
- **Evaluation Dataset:** FER-2013 PrivateTest Set (3,589 face crops)
- **Official Test Accuracy:** **65.90%** (0.6590) — matching benchmark human consensus (~65% on FER-2013)
- **Macro F1-Score:** **0.6401** (Weighted Average F1: **0.6552**)
- **Per-Class F1 Breakdown:**
  - Happy: **85.97%**
  - Surprise: **74.07%**
  - Neutral: **65.56%**
  - Disgust: **65.42%**
  - Angry: **58.87%**
  - Sad: **51.51%**
  - Fear: **46.63%**

*Full evaluation report available at `results/metrics_report.txt` and confusion matrix at `results/confusion_matrix.png`.*

---

## 💻 Team Member Guide: Setup & Run in VS Code

Follow these step-by-step instructions to open and run FaceForge on your local machine:

### Step 1: Open Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File** ➔ **Open Folder...** (or press `Ctrl + K, Ctrl + O`).
3. Select the `Face_Forge` project root folder (the folder containing `app.py`).
4. Open the integrated terminal in VS Code: **Terminal** ➔ **New Terminal** (`Ctrl + ` ` `).

### Step 2: Create a Python 3.12 Virtual Environment
> [!IMPORTANT]
> **Use Python 3.12.** TensorFlow currently does not provide compatible wheels for Python 3.14.

In the VS Code terminal, run:
```powershell
# Create virtual environment named .venv using Python 3.12
py -3.12 -m venv .venv

# Activate the virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# If PowerShell shows an Execution_Policy error, run this first:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# Windows Command Prompt (CMD):
.\.venv\Scripts\activate.bat
```

### Step 3: Select the Python Interpreter in VS Code
1. Press `Ctrl + Shift + P` to open the Command Palette.
2. Type **`Python: Select Interpreter`** and press `Enter`.
3. Select the interpreter pointing to your newly created virtual environment:
   `Python 3.12.x ('.venv': venv) .\.venv\Scripts\python.exe`.

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```
> [!NOTE]
> `requirements.txt` is pre-configured with strictly compatible versions (`opencv-contrib-python==4.14.0.94`, `tensorflow==2.21.0`, `fer==25.10.3`, `fastapi`, `uvicorn`, etc.). **Do not manually install `opencv-python`**, as it conflicts with `opencv-contrib-python`.

### Step 5: Run the Project
Choose either option:

- **Option A (Terminal Command):**
  ```powershell
  python app.py
  ```
- **Option B (One-Click Batch Launcher):**
  Double-click `run_faceforge.bat` in the project root.

Now open your web browser (Chrome, Edge, or Firefox) and visit:
👉 **`http://127.0.0.1:8000`**

### Step 6: Verify the Setup
Run the automated verification script to confirm everything is running properly:
```powershell
python test_system_verification.py
```
*(All 8 tests should output `PASS` with 0 errors).*

---

## 🔒 Security & Data Integrity Features

1. **Zero Artificial Faces:** Empty scenes or non-face images accurately yield `0 faces detected` without fabricating fallback bounding boxes.
2. **Admin PIN Authentication:** Dangerous operations (clearing inference logs at `DELETE /api/results/clear`) require the Admin Security PIN (`1234`).
3. **CSV Formula Injection Sanitization:** All logged fields starting with `=`, `+`, `-`, or `@` are safely sanitized before persisting to `results/results.csv`.
4. **Asynchronous Video Worker:** Heavy video decoding runs in a background thread pool (`asyncio.to_thread`), preventing server stalls during multi-user access.
5. **Non-Blocking Device Polling:** Physical webcam drivers are not locked during API status polls.

---

## 🧪 Verification & Testing

The project includes both an automated integration test suite and unit tests:

```powershell
# 1. System verification suite (Validates 8 core integration points)
python test_system_verification.py

# 2. Pipeline integration tests (Module 2 + Module 3 in FaceForge)
python -m pytest tests

# 3. Module 3 deep learning unit tests (59 model unit tests)
python -m pytest module3_unit_tests
```

**Tests Covered:**
- Module 2 `float32`/`float64` input robustness
- Non-face blank image 0-face detection (no artificial bounding boxes)
- CSV Formula injection sanitization
- Config validation and boundary clamping
- Admin PIN authentication checks
- Fast status endpoint without camera locks
- Authentic FER-2013 ground-truth evaluation consistency (65.90% accuracy)
- Module 1 CLAHE and tensor formatting

---

## 📄 Documentation Artifacts

- **Dataset Specification PDF:** `FaceForge_FER2013_Dataset_Specification_Report.pdf`
- **SRS Document:** `FaceForge_SRS_Document.md`
- **Confusion Matrix:** `results/confusion_matrix.png`
- **Evaluation Report:** `results/metrics_report.txt`

