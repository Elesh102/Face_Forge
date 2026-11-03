# Integration tests: Module 2 (find_faces) + Module 3 (emotion) inside Face Forge (Module 4)
# Run from the Face Forge folder:  python -m pytest -v tests
import csv
import os

import cv2
import numpy as np
import pytest

import adapter_face
import controller
import module2_detection
from conftest import to_jpg_bytes

SAMPLE_BOX = (177, 66, 95, 95)


def overlap(a, b):
    # intersection over union of two (x, y, w, h) boxes
    ax2, ay2, bx2, by2 = a[0] + a[2], a[1] + a[3], b[0] + b[2], b[1] + b[3]
    iw = max(0, min(ax2, bx2) - max(a[0], b[0]))
    ih = max(0, min(ay2, by2) - max(a[1], b[1]))
    inter = iw * ih
    return inter / (a[2] * a[3] + b[2] * b[3] - inter)


# ---- Module 2 on its own

def test_module2_finds_the_face(sample_bgr):
    boxes = module2_detection.find_faces(sample_bgr)
    assert len(boxes) == 1
    assert overlap(boxes[0], SAMPLE_BOX) > 0.7


def test_module2_no_face_gives_empty_list(blank_bgr):
    assert module2_detection.find_faces(blank_bgr) == []


@pytest.mark.parametrize("bad", [None, "photo.jpg", np.zeros((0, 0, 3), np.uint8)],
                         ids=["none", "string", "empty"])
def test_module2_bad_input_gives_empty_list(bad):
    assert module2_detection.find_faces(bad) == []


@pytest.mark.xfail(strict=False, reason="FINDING: Module 2 crashes on float images (cvtColor)")
def test_module2_float_image_does_not_crash():
    assert module2_detection.find_faces(np.zeros((100, 100, 3), np.float64)) == []


# ---- adapter_face uses Module 2 when use_module2 is on

def test_adapter_uses_module2_boxes(sample_bgr):
    assert adapter_face.detect_faces(sample_bgr, use_real=True) == module2_detection.find_faces(sample_bgr)


def test_adapter_returns_empty_when_module2_finds_nothing(blank_bgr):
    # with the real module on, no face must mean no box (not a fake centered box)
    assert adapter_face.detect_faces(blank_bgr, use_real=True) == []


# ---- adapter_emotion with Module 3: bad crops must not get a made-up emotion

@pytest.mark.parametrize("crop", [np.zeros((80, 80, 3), np.uint8), np.zeros((12, 12, 3), np.uint8)],
                         ids=["black_crop", "tiny_crop"])
def test_adapter_emotion_bad_crop_is_not_guessed(crop):
    import adapter_emotion
    rec = adapter_emotion.predict_face(crop, box=(0, 0, crop.shape[1], crop.shape[0]), use_real=True)
    assert rec["face_found"] is False
    assert rec["emotion"] == "unknown" and rec["confidence"] == 0.0


def run_in_threads(fn, n_threads=6, repeats=30):
    import threading
    wrong = []

    def worker():
        for _ in range(repeats):
            if not fn():
                wrong.append(1)

    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return len(wrong)


def test_module3_in_threads_gives_correct_answers(sample_bgr):
    import adapter_emotion
    crop = adapter_face.crop_face(sample_bgr, SAMPLE_BOX)
    expected = adapter_emotion.predict_face(crop, box=SAMPLE_BOX, use_real=True)["scores"]
    assert run_in_threads(
        lambda: adapter_emotion.predict_face(crop, box=SAMPLE_BOX, use_real=True)["scores"] == expected) == 0


@pytest.mark.xfail(strict=False, reason="FINDING #16: Module 2 shares one CascadeClassifier, boxes change in threads")
def test_module2_in_threads_gives_same_boxes(sample_bgr):
    expected = module2_detection.find_faces(sample_bgr)
    assert run_in_threads(lambda: module2_detection.find_faces(sample_bgr) == expected) == 0


# ---- full pipeline: image

def test_image_pipeline_live(live_mode, sample_bgr, temp_results):
    out = controller.process_single_image(to_jpg_bytes(sample_bgr), "astro.jpg", "image")
    assert out["data_source"] == "live"
    assert out["total_faces"] == 1
    rec = out["records"][0]
    assert rec["emotion"] == "happy" and rec["face_found"] is True
    assert overlap(rec["box"], SAMPLE_BOX) > 0.7
    assert abs(sum(rec["scores"].values()) - 1) <= 0.05

    rows = list(csv.DictReader(open(temp_results, encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["emotion"] == "happy" and rows[0]["data_source"] == "live"


def test_image_pipeline_is_repeatable(live_mode, sample_bgr):
    # real model: same picture -> same answer (the mock gave random answers)
    a = controller.process_single_image(to_jpg_bytes(sample_bgr), "a.jpg", "image")
    b = controller.process_single_image(to_jpg_bytes(sample_bgr), "b.jpg", "image")
    assert a["records"][0]["scores"] == b["records"][0]["scores"]


def test_image_pipeline_two_faces(live_mode, sample_bgr):
    two = cv2.hconcat([sample_bgr, cv2.flip(sample_bgr, 1)])
    out = controller.process_single_image(to_jpg_bytes(two), "two.jpg", "image")
    assert out["total_faces"] == 2
    assert [r["emotion"] for r in out["records"]] == ["happy", "happy"]


@pytest.mark.xfail(strict=False, reason="FINDING: controller adds a fake centered box when no face is found")
def test_image_pipeline_no_face_gives_no_records(live_mode, blank_bgr):
    out = controller.process_single_image(to_jpg_bytes(blank_bgr), "blank.jpg", "image")
    assert out["total_faces"] == 0


def test_image_pipeline_rejects_garbage(live_mode):
    with pytest.raises(ValueError):
        controller.process_single_image(b"not an image", "x.jpg", "image")


def test_demo_mode_still_uses_mock(demo_mode, sample_bgr):
    out = controller.process_single_image(to_jpg_bytes(sample_bgr), "astro.jpg", "image")
    assert out["data_source"] == "demo"


# ---- webcam frame and video

def test_webcam_frame_live(live_mode, sample_bgr):
    out = controller.process_webcam_frame(to_jpg_bytes(sample_bgr))
    assert [r["emotion"] for r in out["records"]] == ["happy"]


def test_webcam_frame_without_face(live_mode, blank_bgr):
    assert controller.process_webcam_frame(to_jpg_bytes(blank_bgr))["records"] == []


def test_video_pipeline_live(live_mode, sample_bgr, blank_bgr, tmp_path):
    path = str(tmp_path / "clip.avi")
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MJPG"), 10, (512, 512))
    blank = cv2.resize(blank_bgr, (512, 512))
    for i in range(30):  # frames 0-9 face, 10-19 blank, 20-29 face
        writer.write(blank if 10 <= i < 20 else sample_bgr)
    writer.release()

    out = controller.process_video_file(path, "clip.avi", sampling_step=10)
    frames = [(r["frame_number"], r["emotion"]) for r in out["records"]]
    assert frames == [(0, "happy"), (20, "happy")]  # nothing for the blank frame
