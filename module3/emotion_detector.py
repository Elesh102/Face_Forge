# Module 3 - emotion detection using the pretrained FER model
#
# Usage:
#   detector = EmotionDetector()
#   result = detector.predict("photo.jpg")            # finds faces itself
#   result = detector.predict_face_crop(crop)         # image is already a face
#   result = detector.predict_with_boxes(frame, boxes)  # faces found by Module 2
#
# result = {"status": "ok" / "no_face" / "error", "error": ..., "num_faces": n,
#           "faces": [{"box": [x, y, w, h], "dominant_emotion": "happy",
#                      "score": 0.98, "scores": {...7 emotions...}}]}

import os
import threading
import warnings

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")  # hide tensorflow info logs

import cv2
import numpy as np

with warnings.catch_warnings():
    warnings.simplefilter("ignore")  # fer prints a pkg_resources warning on import
    import fer
    from fer.fer import FER  # in fer 25.x this does not work: from fer import FER

# same order as fer uses internally (checked in smoke_test_fer.py)
EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

MIN_FACE_SIZE = 30  # px; smaller faces give random answers (Module 2 also uses minSize 30)
BLANK_STD = 2.0     # a crop whose pixels barely change (all black / white / gray) is not a face

# fer keeps ONE model for all FER objects and it is not thread safe:
# two threads at once got wrong scores, so only one thread may use it at a time
model_lock = threading.Lock()


class EmotionDetector:
    def __init__(self, use_tflite=True, mtcnn=False):
        # load the model only once, it takes a few seconds
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # tf.lite deprecation warning
            self.fer = FER(mtcnn=mtcnn, use_tflite=use_tflite)
            # for crops: no extra 10px grey border around the face. With the border,
            # FER-2013 PublicTest accuracy was 50.2%, without it 65.4%
            self.fer_crop = FER(use_tflite=use_tflite, offsets=(0, 0))

        self.model_info = {
            "package": "fer",
            "version": fer.__version__,
            "backend": "tflite" if use_tflite else "keras",
            "face_detector": "mtcnn" if mtcnn else "haar",
        }

    def predict(self, image):
        return self.run(image, None)

    def predict_face_crop(self, face_crop):
        # whole image is treated as one face, so no face detection
        try:
            img = load_bgr_image(face_crop)
        except (ValueError, TypeError) as e:
            return make_result("error", error=str(e))
        h, w = img.shape[:2]
        if w < MIN_FACE_SIZE or h < MIN_FACE_SIZE:
            return make_result("error", error=f"crop too small ({w}x{h}), need at least "
                                              f"{MIN_FACE_SIZE}x{MIN_FACE_SIZE}")
        if cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).std() < BLANK_STD:
            return make_result("no_face", error="crop is blank (no face in it)")
        return self.run(img, [(0, 0, w, h)], model=self.fer_crop)

    def predict_with_boxes(self, image, boxes):
        # boxes come from Module 2 as (x, y, w, h)
        try:
            boxes = [tuple(int(v) for v in b) for b in boxes]
        except (ValueError, TypeError) as e:
            return make_result("error", error=f"bad boxes: {e}")
        if len(boxes) == 0:
            return make_result("no_face", error="no face boxes given")
        for b in boxes:
            if len(b) != 4 or b[2] <= 0 or b[3] <= 0:
                return make_result("error", error=f"bad box {list(b)}, need (x, y, w, h)")
            if b[2] < MIN_FACE_SIZE or b[3] < MIN_FACE_SIZE:
                return make_result("error", error=f"box {list(b)} too small, need at least "
                                                  f"{MIN_FACE_SIZE}x{MIN_FACE_SIZE}")
        return self.run(image, boxes)

    def run(self, image, boxes, model=None):
        model = model or self.fer
        try:
            img = load_bgr_image(image)
        except (ValueError, TypeError) as e:
            return make_result("error", error=str(e))

        h, w = img.shape[:2]
        for x, y, bw, bh in boxes or []:
            if x >= w or y >= h or x + bw <= 0 or y + bh <= 0:
                return make_result("error", error=f"box {[x, y, bw, bh]} is outside the image")

        try:
            with model_lock, warnings.catch_warnings():
                warnings.simplefilter("ignore")
                raw = model.detect_emotions(img, face_rectangles=boxes)
        except Exception as e:
            return make_result("error", error=f"model error: {e}")

        if len(raw) == 0:
            return make_result("no_face", error="no face detected")

        faces = []
        for r in raw:
            scores = {e: float(r["emotions"][e]) for e in EMOTIONS}
            top = max(EMOTIONS, key=lambda e: scores[e])
            faces.append({
                "box": [int(v) for v in r["box"]],  # numpy ints -> normal ints for json
                "dominant_emotion": top,
                "score": scores[top],
                "scores": scores,
            })
        return make_result("ok", faces=faces)


def make_result(status, faces=None, error=None):
    faces = faces or []
    return {"status": status, "error": error, "num_faces": len(faces), "faces": faces}


def load_bgr_image(image):
    # accepts a file path or a numpy image, always returns a 3 channel BGR image
    if isinstance(image, (str, os.PathLike)):
        if not os.path.isfile(image):
            raise ValueError(f"image file not found: {image}")
        # cv2.imread fails on some windows paths, imdecode works for all
        img = cv2.imdecode(np.fromfile(image, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"could not read image: {image}")
        return img

    if not isinstance(image, np.ndarray):
        raise TypeError(f"image must be a path or numpy array, not {type(image).__name__}")
    if image.size == 0:
        raise ValueError("image is empty")
    if image.dtype != np.uint8:
        raise ValueError(f"image must be uint8, got {image.dtype}")

    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    channels = image.shape[2]
    if channels == 1:
        return cv2.cvtColor(image[:, :, 0], cv2.COLOR_GRAY2BGR)
    if channels == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    if channels == 3:
        return image
    raise ValueError(f"unsupported image shape {image.shape}")


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("usage: python module3\\emotion_detector.py <image> [--crop]")
        sys.exit()
    detector = EmotionDetector()
    if "--crop" in sys.argv:
        result = detector.predict_face_crop(sys.argv[1])
    else:
        result = detector.predict(sys.argv[1])
    print(json.dumps(result, indent=2))
