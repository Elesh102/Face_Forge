# Module 3 Integration Contract

**From:** Module 3 (Emotion Recognition & Model Evaluation)
**For:** Module 2 (Face & Input Processing), Module 4 (System Integration, UI & Analytics)
**Status:** Proposed. Please reply with changes before we integrate.

Module 3 is a plain Python module. It never opens a window, a camera, a video file, or a database. Modules 2 and 4 handle those and call Module 3 only to get emotions.

## 0. Face Forge quick start (Module 4)

This follows the contract in `FaceForge_Teammate_Integration_Guide.pdf`:

1. Copy the `module3/` folder into the Face Forge root, next to `controller.py`.
2. In `adapter_emotion.py`, replace the mock lines at the integration point with:
   ```python
   from module3.module3_model import predict_emotion
   scores = predict_emotion(face_img)   # dict of 7 floats, sums to ~1
   ```
   `predict_emotion` raises `ValueError` if it cannot predict (empty, blank, smaller than 30×30, or invalid crop). It never returns random scores. `run_inference` is the same function under the name used in Module 4's newer spec.
3. Set `use_module3: true` **and** `demo_mode: false` in `config.yaml`.
4. No weights file is needed. `fer` ships its own pretrained model inside the pip package.
5. Evaluation files for the Evaluation page: copy `module3/reports/metrics_report.txt` and `module3/reports/confusion_matrix.png` into Face Forge `results/`, replacing the placeholder report. Result on FER-2013 PrivateTest (3,589 images): accuracy 0.659.

Not yet tested inside the Face Forge app. Only `predict_emotion` itself is tested (`tests/test_module3_model.py`).

## 1. Setup (whole team)

| Item | Value |
|---|---|
| Python | **3.12** (64-bit). TensorFlow has no Windows build for Python 3.14. |
| Install | `pip install -r module3/requirements-module3.txt` |
| OpenCV | `opencv-contrib-python==4.14.0.94`. **Do not use OpenCV 5.0**: it breaks fer's face detector. Please use the same version in Modules 2 and 4. |
| setuptools | `<81` (fer 25.10.3 needs `pkg_resources`) |

## 2. How to call Module 3

```python
from module3.emotion_detector import EmotionDetector

detector = EmotionDetector()   # loads the model, takes a few seconds; create it ONCE at app start
```

Pick the method that matches what you already have:

| You have... | Call | Face detection done by |
|---|---|---|
| A full image or frame, no faces found yet | `detector.predict(frame)` | Module 3 (fer's Haar cascade) |
| A full frame **and** face boxes from Module 2 | `detector.predict_with_boxes(frame, boxes)` | Module 2 |
| Only a cropped face image | `detector.predict_face_crop(crop)` | Module 2 |

**Recommended for Module 2:** `predict_with_boxes(frame, boxes)`. It keeps the context around the face that the model expects, and the returned boxes are already in frame coordinates.

## 3. Input rules (Module 2 → Module 3)

| Rule | Detail |
|---|---|
| Image type | NumPy array `uint8` (0–255), or a file path (`str` / `Path`). |
| Colour order | **BGR** (OpenCV default: `cv2.imread`, `cv2.VideoCapture.read`). Grayscale (H×W) and BGRA are also accepted. **RGB is NOT detected automatically.** If the frame comes from PIL, MediaPipe, or similar, convert it first with `cv2.cvtColor(img, cv2.COLOR_RGB2BGR)`. |
| Size | Any size. The model internally resizes each face to 64×64 grayscale. |
| Boxes | List of `(x, y, w, h)` in pixels: top-left corner plus width and height, the same format as `cv2.CascadeClassifier.detectMultiScale`. A NumPy array of boxes is fine. Boxes in `(x1, y1, x2, y2)` format must be converted: `w = x2 - x1`, `h = y2 - y1`. |
| Crops | If you send crops, include a small margin around the face, not a tight cut. Crops or boxes smaller than **30×30 px** return `status: "error"` ("too small"). A blank crop (all one colour) returns `status: "no_face"`. |
| Threads | Safe to call from several threads. fer shares one model, so Module 3 lets only one thread use it at a time (calls wait for each other). |

## 4. Output (Module 3 → Module 4)

Every method returns the same JSON-serialisable `dict`:

```json
{
  "status": "ok",
  "error": null,
  "num_faces": 1,
  "faces": [
    {
      "box": [177, 66, 95, 95],
      "dominant_emotion": "happy",
      "score": 1.0,
      "scores": {"angry": 0.0, "disgust": 0.0, "fear": 0.0, "happy": 1.0,
                 "sad": 0.0, "surprise": 0.0, "neutral": 0.0}
    }
  ]
}
```

Model details (package, version, backend) are available as `detector.model_info`.

| Field | Meaning |
|---|---|
| `status` | `"ok"` = at least one face predicted. `"no_face"` = no face found (not an error; just show "no face"). `"error"` = bad input or model failure; the reason is in `error`. **Always check `status` first.** |
| `faces` | One entry per face. Empty unless `status == "ok"`. Order is not guaranteed; identify faces by `box`. |
| `box` | `[x, y, w, h]` in pixels of the image you passed in. For `predict_face_crop` it is `[0, 0, crop_w, crop_h]`, so add your crop offset to draw it on the frame. |
| `dominant_emotion` | One of the 7 classes, always lowercase English. |
| `score` | The model's softmax output for the dominant emotion, 0–1, rounded to 2 decimals. Show it as "model score", **not** "accuracy" or "confidence %". |
| `scores` | All 7 class scores, always in the same order. They sum to about 1. |

The function **never raises** for bad input or no face. It returns `status` `"error"` or `"no_face"` instead.

## 5. Example: webcam / video loop (for Module 2 / 4)

Example only. Module 3 has not tested this with a real camera; capture and display belong to Modules 2 and 4.

```python
import cv2
from module3.emotion_detector import EmotionDetector

detector = EmotionDetector()
cap = cv2.VideoCapture(0)
while True:
    ok, frame = cap.read()                      # BGR frame
    if not ok:
        break
    result = detector.predict(frame)            # or predict_with_boxes(frame, module2_boxes)
    if result["status"] == "ok":
        for face in result["faces"]:
            x, y, w, h = face["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)
            cv2.putText(frame, f"{face['dominant_emotion']} {face['score']:.2f}",
                        (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)
    cv2.imshow("emotions", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()
```

## 6. Speed (indicative only)

Measured on one laptop (Intel 64-bit CPU, Windows 11, Python 3.12, TFLite backend). Each figure is the median of 30 runs on the sample image after warm-up:

| Call | Median time |
|---|---|
| `predict()` on a 640×480 frame (face detection + emotion) | ~15 ms |
| `predict_with_boxes()` with 1 box (emotion only) | ~0.5 ms |
| `predict_face_crop()` on a 95×95 crop | ~0.4 ms |

Most of the time is spent on face detection, not on the emotion model. These figures are a rough guide, not a benchmark; they will differ on other machines and with more faces.

## 7. Questions for the team

- **Module 2:** Which face detector do you use, and what box format does it return? Will you send boxes (preferred) or crops?
- **Module 4:** Is this output schema OK to store as-is (JSON)? Do you also need a timestamp or frame number? (Proposal: Module 4 adds those, since Module 3 does not know the time or frame index.)
- **Module 1:** Labelled test data format: CSV `image_path,true_label` or one folder per emotion. What label names will you use, and where does the data come from? (See README → Evaluation.)
