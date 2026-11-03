FACE FORGE - MODULE 3 (EMOTION MODEL) HANDOFF
==============================================

WHAT IS IN THIS ZIP
-------------------
put_in_faceforge_root\      -> copy everything in here into the Face Forge root folder
                               (the folder that has app.py and controller.py)
  module3\                  Module 3 code (emotion model + evaluation) and reports
  adapter_emotion.py        Module 3 plugged in   (replaces your adapter_emotion.py)
  adapter_face.py           Module 2 plugged in   (replaces your adapter_face.py)
  module2_detection.py      Module 2 file, exactly as Module 2 sent it
  config.yaml               demo_mode: false, use_module2: true, use_module3: true
  results\metrics_report.txt   REAL evaluation report (replaces the placeholder)
  results\confusion_matrix.png REAL confusion matrix
  tests\                    integration tests (Module 2 + 3 inside Face Forge)
module3_unit_tests\         Module 3's own unit tests (59 tests). Optional: copy this folder
                               into the Face Forge root too, then run them (step 4)

STEPS
-----
1. Python 3.12 (TensorFlow does not install on Python 3.14).
2. Copy the contents of put_in_faceforge_root\ into the Face Forge root. Overwrite when asked.
3. Install:
     py -3.12 -m venv venv
     venv\Scripts\python.exe -m pip install -r module3\requirements-module3.txt
     venv\Scripts\python.exe -m pip install fastapi uvicorn python-multipart pyyaml pandas pillow
   Use opencv-contrib-python==4.14.0.94 only. Do NOT also install opencv-python:
   both packages provide cv2 and break each other. OpenCV 5.0 breaks the Haar face detector.
4. Check:
     venv\Scripts\python.exe -m pytest tests                -> 18 passed, 3 xfailed
     venv\Scripts\python.exe -m pytest module3_unit_tests   -> 59 passed
       (only after copying module3_unit_tests\ into the Face Forge root;
        it needs the module3\ folder next to it)
5. Run:
     venv\Scripts\python.exe -m uvicorn app:app --port 8000   -> http://127.0.0.1:8000
   The badge should say "Live module". The same photo gives the same emotion every time.

MODULE 3 FUNCTIONS
------------------
from module3.module3_model import run_inference      (same as predict_emotion)
scores = run_inference(face_crop)   # dict of 7 scores, sums to ~1
- Raises ValueError for a bad crop (empty, blank, smaller than 30x30). It never returns random scores.
- No weights file is needed. The pretrained model is inside the "fer" pip package.
- Classes: angry, disgust, fear, happy, sad, surprise, neutral

EVALUATION RESULT (for the Evaluation page)
-------------------------------------------
FER-2013 PrivateTest, 3,589 face images: accuracy 65.9 %, macro F1 0.640.
Details: module3\reports\metrics_report.txt and module3\reports\error_analysis.md
The old results\metrics_report.txt (ResNet-50, 0.834) was a placeholder. Please replace it.

THE 3 "XFAILED" TESTS ARE KNOWN ISSUES (not caused by Module 3)
---------------------------------------------------------------
- controller.py: when no face is found in an image, it adds a fake centered box and shows an emotion for it
- module2_detection.py: crashes on float images
- module2_detection.py: one shared CascadeClassifier, boxes change slightly when used from several threads
