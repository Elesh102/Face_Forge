# Module 3: Emotion Recognition & Model Evaluation

Wraps the pretrained [`fer`](https://github.com/justinshenk/fer) facial-expression model (no training) and evaluates it on labelled data.
Teammates: see **[INTEGRATION.md](INTEGRATION.md)** for how to call this module.

## Files

| File | Purpose |
|---|---|
| `emotion_detector.py` | `EmotionDetector` class: the only thing other modules import |
| `smoke_test_fer.py` | Prints fer's raw output on one image (used to verify the API) |
| `model_test.py` | Runs the detector on a folder of sample images and records predictions and timing (**no accuracy**) |
| `evaluation.py` | Accuracy, precision, recall, F1 and confusion matrix on a **labelled** test set |
| `fer2013_to_folder.py` | Turns Module 1's `fer2013.csv` into `happy\`, `sad\` … image folders for `evaluation.py` |
| `module3_model.py` | `predict_emotion()` / `run_inference()`: the functions Face Forge (Module 4) calls |
| `reports/` | `metrics_report.txt`, `confusion_matrix.png`, `predictions.csv`, `error_analysis.md` |
| `sample_inputs/` | Images for smoke tests only |
| `requirements-module3.txt` | Direct dependencies (`.lock.txt` lists every package version that was verified) |
| `../tests/` | pytest tests |

## Setup (Windows, PowerShell)

```powershell
py -3.12 -m venv F:\venvs\emotion-m3
F:\venvs\emotion-m3\Scripts\python.exe -m pip install -r module3\requirements-module3.txt
```

- Use **Python 3.12**. TensorFlow has no Windows build for 3.14.
- The venv is outside OneDrive on purpose. About 2 GB of small files would otherwise sync.
- In VS Code, select the interpreter `F:\venvs\emotion-m3\Scripts\python.exe` (`.vscode/settings.json` already points to it).

Two compatibility fixes are pinned in the requirements. Both were found while testing:

1. `setuptools<81`: fer 25.10.3 imports `pkg_resources`, which was removed in setuptools 81+.
2. `opencv-contrib-python==4.14.0.94`: with OpenCV 5.0, `cv2.data` has no Haar cascade files, so fer's default face detector fails.

## Run

All commands run from the project root.

```powershell
# 1. Tests (expected: all pass)
F:\venvs\emotion-m3\Scripts\python.exe -m pytest -v

# 2. One image -> JSON result
F:\venvs\emotion-m3\Scripts\python.exe module3\emotion_detector.py module3\sample_inputs\astronaut_nasa.png

# 3. All sample images -> reports\sample_predictions.csv
F:\venvs\emotion-m3\Scripts\python.exe module3\model_test.py

# 4a. FER-2013 (Module 1): csv -> folders, then evaluate the PrivateTest split
F:\venvs\emotion-m3\Scripts\python.exe module3\fer2013_to_folder.py path\to\fer2013.csv --usage PrivateTest --out data\fer2013_private
F:\venvs\emotion-m3\Scripts\python.exe module3\evaluation.py --folder data\fer2013_private --crop --dataset-name "FER-2013 PrivateTest"

# 4. Formal evaluation on any other labelled data
F:\venvs\emotion-m3\Scripts\python.exe module3\evaluation.py --csv path\to\labels.csv --dataset-name "Module 1 test set v1"
F:\venvs\emotion-m3\Scripts\python.exe module3\evaluation.py --folder path\to\test_set --dataset-name "Module 1 test set v1"
```

## Verified model facts (fer 25.10.3, read from the installed source)

- Import with `from fer.fer import FER`. The tutorial form `from fer import FER` does not work in 25.x.
- 7 classes, in this order: angry, disgust, fear, happy, sad, surprise, neutral.
- Input: each face is converted to 64×64 grayscale. Default backend: quantized TFLite model.
- Output layer: **softmax**, so the 7 scores sum to about 1. fer rounds each score to 2 decimals. The score is **not** a calibrated probability.
- Box format: `(x, y, w, h)` in pixels.
- The package credits Octavio Arriaga's `face_classification` repo and references FER-2013. The exact training split is not documented.

## Evaluation notes

- **Input format:** a CSV with columns `image_path,true_label` (paths can be relative to the CSV), **or** one sub-folder per label.
- **Labels:** these are lowercased and must match the 7 classes. Otherwise the script stops. Use `--label-map "surprised=surprise"` to rename labels, or `--skip-unknown` to drop classes the model doesn't have (e.g. `contempt`).
- **Input mode:** use `--crop` only when the images are already cropped faces (e.g. FER-2013 48×48 images, which are below the Haar detector's 50 px minimum). Don't use it for full photos.
- **Two accuracies are reported:**
  - *on predicted samples*: only images where a face was found.
  - *end-to-end*: no-face and error count as wrong.
- **Averages:** macro and weighted averages are taken over the classes that have predicted samples. The report states which classes those are.
- **FER-2013 split (checked 2026-11-02):** the original training script of the model (oarriaga/face_classification `train_emotion_classifier.py` + `utils/datasets.py`) loads all 35,887 rows and trains on the first 80 %. That is exactly the 28,709 `Training` rows, so **PrivateTest was not used for training**. PublicTest + PrivateTest were the validation data used to pick the best checkpoint, so the PrivateTest score may be slightly optimistic. Write this in the report.
- **Result (2026-11-03):** FER-2013 PrivateTest, 3,589 face crops: **accuracy 0.659**, macro F1 0.640, weighted F1 0.655. Details: `reports/metrics_report.txt`, `reports/confusion_matrix.png`, `reports/error_analysis.md`.
- **Crop setting:** `predict_face_crop` gives the crop to the model with no extra border. fer's default 10 px grey border dropped PublicTest accuracy from 0.654 to 0.502. The setting was chosen on PublicTest, then PrivateTest was run once.
- **Data:** `fer2013.csv` from a Hugging Face mirror (`MoAamir28/FER2013`). MD5 `f8428a1edbd21e88f42c73edd2a14f95` is the same as the original Kaggle file. Kept at `F:\datasets\fer2013\` and not part of the project files (300 MB).
