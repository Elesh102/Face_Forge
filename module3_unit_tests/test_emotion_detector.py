# Tests for emotion_detector.py - checks the code works and the output format is right.
# Not an accuracy test. Run with:  python -m pytest -v
import json
import math
import os
import threading

import cv2
import numpy as np
import pytest

from module3.emotion_detector import EMOTIONS, EmotionDetector, load_bgr_image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(ROOT, "module3", "sample_inputs", "astronaut_nasa.png")
SAMPLE_BOX = (177, 66, 95, 95)  # face box fer found in the smoke test


@pytest.fixture(scope="module")
def detector():
    return EmotionDetector()  # load model once for all tests


@pytest.fixture(scope="module")
def sample_bgr():
    img = cv2.imread(SAMPLE)
    assert img is not None
    return img


def assert_valid_face(face):
    assert face["dominant_emotion"] in EMOTIONS
    assert list(face["scores"]) == EMOTIONS
    assert all(math.isfinite(s) and 0 <= s <= 1 for s in face["scores"].values())
    # scores are rounded to 2 decimals so the sum is not exactly 1
    assert abs(sum(face["scores"].values()) - 1.0) <= 0.05
    assert face["score"] == max(face["scores"].values())
    assert face["score"] == face["scores"][face["dominant_emotion"]]
    assert len(face["box"]) == 4 and all(type(v) is int for v in face["box"])


def assert_result_shape(result):
    assert set(result) == {"status", "error", "num_faces", "faces"}
    assert result["num_faces"] == len(result["faces"])
    json.dumps(result)  # Module 4 must be able to store/send it as JSON


# valid input

def test_predict_from_path(detector):
    result = detector.predict(SAMPLE)
    assert_result_shape(result)
    assert result["status"] == "ok" and result["error"] is None
    assert result["num_faces"] == 1
    assert_valid_face(result["faces"][0])


def test_sample_smile_is_happy(detector):
    # Sanity check on one clearly smiling face (a regression check, not accuracy)
    assert detector.predict(SAMPLE)["faces"][0]["dominant_emotion"] == "happy"


def test_path_and_array_give_same_result(detector, sample_bgr):
    assert detector.predict(SAMPLE)["faces"] == detector.predict(sample_bgr)["faces"]


@pytest.mark.parametrize("convert", [cv2.COLOR_BGR2GRAY, cv2.COLOR_BGR2BGRA], ids=["gray", "bgra"])
def test_grayscale_and_bgra_accepted(detector, sample_bgr, convert):
    result = detector.predict(cv2.cvtColor(sample_bgr, convert))
    assert result["status"] == "ok"
    assert_valid_face(result["faces"][0])


def test_multiple_faces(detector, sample_bgr):
    two = cv2.hconcat([sample_bgr, cv2.flip(sample_bgr, 1)])
    result = detector.predict(two)
    assert result["status"] == "ok"
    assert result["num_faces"] == 2
    for face in result["faces"]:
        assert_valid_face(face)


def test_face_crop(detector, sample_bgr):
    x, y, w, h = SAMPLE_BOX
    crop = sample_bgr[y:y + h, x:x + w]
    result = detector.predict_face_crop(crop)
    assert_result_shape(result)
    assert result["status"] == "ok"
    assert result["num_faces"] == 1
    assert result["faces"][0]["box"] == [0, 0, w, h]
    assert_valid_face(result["faces"][0])


def test_predict_with_boxes_matches_own_detection(detector, sample_bgr):
    result = detector.predict_with_boxes(sample_bgr, [SAMPLE_BOX])
    assert_result_shape(result)
    assert result["status"] == "ok"
    assert result["faces"][0]["box"] == list(SAMPLE_BOX)  # frame coordinates kept
    # same box as fer's own detector -> same prediction as predict()
    assert result["faces"] == detector.predict(sample_bgr)["faces"]


def test_predict_with_boxes_accepts_numpy_boxes(detector, sample_bgr):
    boxes = np.array([SAMPLE_BOX], dtype=np.int32)  # e.g. straight from cv2.detectMultiScale
    assert detector.predict_with_boxes(sample_bgr, boxes)["status"] == "ok"


def test_predict_with_no_boxes_is_no_face(detector, sample_bgr):
    assert detector.predict_with_boxes(sample_bgr, [])["status"] == "no_face"


@pytest.mark.parametrize("boxes", [
    [(10, 10, 0, 50)],
    [(10, 10, 50)],
    [(5000, 5000, 50, 50)],
], ids=["zero_width", "three_values", "outside_image"])
def test_predict_with_bad_boxes(detector, sample_bgr, boxes):
    result = detector.predict_with_boxes(sample_bgr, boxes)
    assert result["status"] == "error" and result["error"]


# no face / bad input

def test_blank_image_gives_no_face(detector):
    result = detector.predict(np.full((300, 300, 3), 128, np.uint8))
    assert_result_shape(result)
    assert result["status"] == "no_face"
    assert result["faces"] == []


def test_missing_file(detector):
    result = detector.predict(os.path.join(ROOT, "does_not_exist.jpg"))
    assert result["status"] == "error"
    assert "not found" in result["error"]


def test_file_that_is_not_an_image(detector, tmp_path):
    bad = tmp_path / "fake.jpg"
    bad.write_text("this is not an image")
    result = detector.predict(str(bad))
    assert result["status"] == "error"
    assert "could not read image" in result["error"]


@pytest.mark.parametrize("bad_input", [
    None,
    123,
    np.zeros((0, 0, 3), np.uint8),
    np.zeros((100, 100, 3), np.float32),
    np.zeros((100, 100, 5), np.uint8),
], ids=["none", "int", "empty", "float_dtype", "five_channels"])
def test_invalid_inputs_do_not_crash(detector, bad_input):
    for result in (detector.predict(bad_input), detector.predict_face_crop(bad_input)):
        assert_result_shape(result)
        assert result["status"] == "error"
        assert result["error"]


# finding #1: using the model from many threads must not mix up answers

def test_threads_get_correct_answers(detector, sample_bgr):
    x, y, w, h = SAMPLE_BOX
    face = sample_bgr[y:y + h, x:x + w]
    other = cv2.flip(cv2.resize(sample_bgr, (95, 95)), 0)  # a different picture, different scores
    expected = {"face": detector.predict_face_crop(face)["faces"][0]["scores"],
                "other": detector.predict_face_crop(other)["faces"][0]["scores"]}
    second = EmotionDetector()  # fer shares one model between all detectors
    wrong = []

    def worker(k):
        for i in range(100):
            name, img = ("face", face) if (i + k) % 2 else ("other", other)
            d = detector if k % 2 else second
            r = d.predict_face_crop(img)
            if r["status"] != "ok" or r["faces"][0]["scores"] != expected[name]:
                wrong.append(name)

    threads = [threading.Thread(target=worker, args=(k,)) for k in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert wrong == []


# finding #10: crop mode must not give an emotion for things that are clearly not a face

@pytest.mark.parametrize("crop", [
    np.zeros((100, 100, 3), np.uint8),
    np.full((100, 100, 3), 255, np.uint8),
    np.full((60, 60), 128, np.uint8),
], ids=["black", "white", "flat_gray"])
def test_blank_crop_is_no_face(detector, crop):
    result = detector.predict_face_crop(crop)
    assert_result_shape(result)
    assert result["status"] == "no_face"
    assert "blank" in result["error"]


@pytest.mark.parametrize("size", [1, 10, 29], ids=["1px", "10px", "29px"])
def test_too_small_crop_is_error(detector, sample_bgr, size):
    x, y, w, h = SAMPLE_BOX
    crop = cv2.resize(sample_bgr[y:y + h, x:x + w], (size, size))
    result = detector.predict_face_crop(crop)
    assert result["status"] == "error"
    assert "too small" in result["error"]


def test_smallest_allowed_crop_works(detector, sample_bgr):
    x, y, w, h = SAMPLE_BOX
    crop = cv2.resize(sample_bgr[y:y + h, x:x + w], (30, 30))  # Module 2 minSize is 30
    assert detector.predict_face_crop(crop)["status"] == "ok"


def test_fer2013_size_gray_crop_works(detector, sample_bgr):
    x, y, w, h = SAMPLE_BOX
    gray = cv2.cvtColor(sample_bgr[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY)
    assert detector.predict_face_crop(cv2.resize(gray, (48, 48)))["status"] == "ok"


def test_too_small_box_is_error(detector, sample_bgr):
    result = detector.predict_with_boxes(sample_bgr, [(200, 100, 12, 12)])
    assert result["status"] == "error"
    assert "too small" in result["error"]


# crop mode must give the crop to the model as it is (no grey border):
# with fer's 10px border, FER-2013 PublicTest accuracy fell from 65.4% to 50.2%

def test_crop_mode_uses_no_border(detector, sample_bgr):
    import warnings
    from fer.fer import FER
    x, y, w, h = SAMPLE_BOX
    crop = sample_bgr[y:y + h, x:x + w]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        no_border = FER(offsets=(0, 0)).detect_emotions(crop, face_rectangles=[(0, 0, w, h)])[0]["emotions"]
    assert detector.predict_face_crop(crop)["faces"][0]["scores"] == {e: float(no_border[e]) for e in EMOTIONS}


def test_full_image_mode_keeps_fer_default(detector, sample_bgr):
    import warnings
    from fer.fer import FER
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        default = FER().detect_emotions(sample_bgr)[0]["emotions"]
    assert detector.predict(sample_bgr)["faces"][0]["scores"] == {e: float(default[e]) for e in EMOTIONS}


PUBLIC_TEST = r"F:\datasets\fer2013\public_test"


@pytest.mark.skipif(not os.path.isdir(PUBLIC_TEST), reason="FER-2013 PublicTest folder not on this machine")
def test_fer2013_public_test_accuracy(detector):
    # 100 images per class from the validation split (not the PrivateTest we report)
    import glob
    correct = total = 0
    for label in EMOTIONS:
        for path in sorted(glob.glob(os.path.join(PUBLIC_TEST, label, "*.png")))[:100]:
            r = detector.predict_face_crop(path)
            correct += r["status"] == "ok" and r["faces"][0]["dominant_emotion"] == label
            total += 1
    assert correct / total > 0.55


# image loading (no model)

def test_load_bgr_image_converts_to_3_channels(sample_bgr):
    gray = cv2.cvtColor(sample_bgr, cv2.COLOR_BGR2GRAY)
    assert load_bgr_image(gray).shape == sample_bgr.shape
    assert load_bgr_image(gray[:, :, None]).shape == sample_bgr.shape
    assert load_bgr_image(SAMPLE).shape == sample_bgr.shape
