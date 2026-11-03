# Tests for predict_emotion() - the function Module 4 (Face Forge) calls
import os

import cv2
import numpy as np
import pytest

from module3.emotion_detector import EMOTIONS
from module3.module3_model import predict_emotion, run_inference

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(ROOT, "module3", "sample_inputs", "astronaut_nasa.png")


def test_contract_output_on_face_crop():
    img = cv2.imread(SAMPLE)
    crop = img[66:161, 177:272]  # same slicing as Face Forge adapter_face.crop_face
    scores = predict_emotion(crop)
    assert type(scores) is dict
    assert list(scores) == list(EMOTIONS)
    assert all(type(v) is float for v in scores.values())
    assert abs(sum(scores.values()) - 1.0) <= 0.05
    assert max(scores, key=scores.get) == "happy"


@pytest.mark.parametrize("bad", [None, np.zeros((0, 0, 3), np.uint8)], ids=["none", "empty"])
def test_contract_raises_instead_of_fake_scores(bad):
    with pytest.raises(ValueError, match="Module 3 could not predict"):
        predict_emotion(bad)


# Module 4's newer contract calls the same thing run_inference()
def test_run_inference_same_as_predict_emotion():
    img = cv2.imread(SAMPLE)
    crop = img[66:161, 177:272]
    assert run_inference(crop) == predict_emotion(crop)


def test_run_inference_accepts_grayscale_crop():
    img = cv2.imread(SAMPLE, cv2.IMREAD_GRAYSCALE)
    scores = run_inference(img[66:161, 177:272])
    assert list(scores) == EMOTIONS


def test_run_inference_raises_on_bad_input():
    with pytest.raises(ValueError):
        run_inference(None)
