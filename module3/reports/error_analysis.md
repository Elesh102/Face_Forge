# Error Analysis: Module 3 (Pretrained FER)

> **Status: formal evaluation done on 2026-11-03** (FER-2013 PrivateTest, 3,589 images).
> Numbers come from `metrics_report.txt`, `confusion_matrix.png` and `predictions.csv` in this folder.
> Section 2 lists informal observations from sample and synthetic images. They are not part of the evaluation.

## 1. Setup

| Item | Value |
|---|---|
| Model | `fer` 25.10.3, quantized TFLite CNN (64×64 grayscale input, 7-class softmax output) |
| Model origin | fer credits Octavio Arriaga's `face_classification` repo. Its training script loads all 35,887 FER-2013 rows and trains on the first 80 %, which is exactly the 28,709 `Training` rows. PublicTest + PrivateTest were its validation data, used to pick the best checkpoint. |
| Test set | **FER-2013 PrivateTest**: 3,589 images, 48×48 grayscale, labels from the original dataset |
| Data source | `fer2013.csv` (the Kaggle file used in Module 1's notebook), downloaded from a Hugging Face mirror (`MoAamir28/FER2013`). MD5 `f8428a1edbd21e88f42c73edd2a14f95` matches the checksum torchvision uses for the original file. Row and class counts match Module 1's notebook. |
| Images per class | angry 491, disgust 55, fear 528, happy 879, sad 594, surprise 416, neutral 626 |
| Label mapping | FER-2013 numbers 0–6 = angry, disgust, fear, happy, sad, surprise, neutral (same order as the model) |
| Input mode | Face crops (`--crop`): the images are already cropped faces, so no face detection |
| Settings choice | The crop setting (no extra border) was chosen on **PublicTest**, not on PrivateTest (see 3.1) |

## 2. Informal observations (sample images only, not evaluation)

| # | Observation | Evidence |
|---|---|---|
| O1 | A clearly smiling, frontal, well-lit face was predicted `happy` with score 1.0 by both the TFLite and the full Keras model. | `smoke_test_fer.py` |
| O2 | The same face downscaled to a **10×10 crop** was predicted `fear` (score 0.48). Very low resolution gives unreliable predictions. | Stage 3 manual test |
| O3 | A tight 95×95 crop scored `happy` 0.98, against 1.0 when the face was predicted inside the full image. Context around the face changes the score slightly. | Stage 3 manual test |
| O4 | Treating a whole 512×512 portrait as a "face crop" (`--crop` on non-crop images) gave wrong predictions on a dummy set. **The input mode must match the data.** | Stage 5 dummy pipeline check |
| O5 | A blank image returned `no_face` (handled, no crash). | tests |
| O6 | Night photo of a man looking up at the moon (2026-10-17): the Haar detector (fer's and Module 2's) boxed the **moon** as a face, and the "emotion" shown was the moon's (happy 0.46). MTCNN found the real face, which was predicted neutral 0.48 (sad 0.28 second). **A wrong face box gives a wrong emotion, and faces that look up are hard to detect.** | manual debug run |
| O7 | Before the fix, 8 threads predicting at once gave **1403 wrong answers out of 1600**, with no error. fer shares one model between all detectors. Fixed with a lock: 0 wrong. | `test_threads_get_correct_answers` |
| O8 | Before the fix, crop mode gave confident emotions for non-faces: all-black → angry 0.72, a 1×1 pixel → angry 0.72. Fixed: blank → `no_face`, under 30×30 → `error`. Still not caught: random noise (sad 0.61) and a black image with one white dot (angry 0.68). Crop mode trusts that the crop is a face. | break-it test, 2026-11-02 |
| O9 | A very dark (8 % brightness) copy of the smiling face was predicted angry 0.29 instead of happy. Lighting changes the answer. | break-it test |
| O10 | A 6000×6000 upscaled portrait gave 6 faces instead of 1 with fer's own detector. Very large images give false detections. | break-it test |

## 3. Overall results (FER-2013 PrivateTest)

| Metric | Value |
|---|---|
| Images evaluated / predicted / no_face / error | 3,589 / 3,589 / 0 / 0 |
| Accuracy | **0.659** (2,365 of 3,589 correct) |
| Macro precision / recall / F1 | 0.643 / 0.639 / 0.640 |
| Weighted precision / recall / F1 | 0.654 / 0.659 / 0.655 |

All 3,589 real faces passed the blank check (none flagged `no_face`), so the 30 px / blank rules added on 2026-11-02 did not reject any real FER-2013 face.

### 3.1 Why the crop setting matters (found during evaluation)

fer adds a 10-pixel border around a face box before classifying it. For a crop, that border is grey padding, not real image, so the face fills less of the model's input. Measured on **PublicTest** (3,589 images, the validation split):

| Crop setting | PublicTest accuracy |
|---|---|
| fer default (10 px grey border) | 0.502 |
| No border (now used by `predict_face_crop`) | 0.654 |
| Keras model instead of TFLite, no border | 0.656 |

The no-border setting was then used **once** on PrivateTest: 0.659. Choosing the setting on PublicTest keeps PrivateTest a clean test. The PrivateTest score with the old border setting was 0.500.

## 4. Where the model goes wrong

| Class | Recall | Precision | Comment |
|---|---|---|---|
| happy | 0.875 | 0.845 | best class |
| surprise | 0.745 | 0.736 | |
| neutral | 0.695 | 0.621 | many sad faces end up here |
| disgust | 0.636 | 0.673 | only 55 test images, so this number is uncertain; 13 of 55 were predicted angry |
| angry | 0.595 | 0.583 | |
| sad | 0.503 | 0.527 | weak |
| fear | 0.426 | 0.515 | **weakest class** |

Most frequent mistakes. The "what the images show" column comes from looking at 8 example images per pair (`mistake_examples.png`, one row per pair, in this order):

| True → Predicted | Count | What the images show (observed) |
|---|---|---|
| sad → neutral | 127 (21 % of sad) | Mostly mild expressions: closed mouth, little visible frown. Several look neutral to a person too. |
| fear → sad | 92 (17 % of fear) | Hands on the head or face, eyes looking down, head tilted. Hands cover part of the face. |
| neutral → sad | 75 (12 % of neutral) | Head tilted down or eyes looking down or sideways. |
| sad → angry / angry → sad | 69 / 69 | (not inspected image by image) |
| fear → surprise | 55 (10 % of fear) | Wide-open mouth and eyes. Fear and surprise share these features; one example is a side view. |

**Score vs correctness.** The median model score was 0.85 when the prediction was right and 0.54 when it was wrong.

| Score at least | Share of images | Accuracy on those images |
|---|---|---|
| 0.5 | 78 % | 74.0 % |
| 0.7 | 53 % | 84.0 % |
| 0.9 | 31 % | 92.4 % |

A low score is a useful warning sign, but the score is still not a calibrated probability. For example, "0.9" does not mean "90 % sure".

## 5. Failure cases (no_face / error)

None on FER-2013 PrivateTest: all 3,589 crops were predicted. This is expected in crop mode, because no face detection runs. In the full app, failures come from face detection (Module 2), not from this step (see O6).

## 6. Limitations

Measured on the test set:
- **Fear and sad are weak** (recall 0.43 and 0.50). Sad, neutral and fear are often confused with each other.
- **Downward gaze, tilted heads and hands over the face** appear often in the mistakes (section 4).
- **Fear vs surprise:** the open mouth and wide eyes are shared, and 10 % of fear faces were called surprise.

Known but not measured on the test set:
- **Disgust** has only 55 test images, so its score is uncertain.
- **Label noise:** FER-2013 labels were made from web images and are known to be noisy. Microsoft later relabelled it as FER+. Some "mistakes" may be wrong labels.
- **Optimistic estimate:** PrivateTest was part of the validation data used to pick the model's checkpoint (section 1), so 0.659 may be slightly higher than on completely new data.
- **Dataset shift:** FER-2013 images are 48×48 grayscale web photos. Webcam images in Face Forge (colour, different lighting, pose) may score differently. This was not measured.
- **Face detection:** in the full app, a wrong or missing face box (Module 2) gives a wrong or missing emotion (O6). This evaluation does not cover detection.
- **Score meaning:** `score` is a softmax output, not a calibrated probability.
