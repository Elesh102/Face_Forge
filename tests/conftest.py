import os
import sys

import cv2
import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import controller  # noqa: E402
import storage  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "data")
LIVE_CONFIG = {"demo_mode": False, "use_module1": False, "use_module2": True,
               "use_module3": True, "confidence_threshold": 0.5, "video_sampling_step": 10}


@pytest.fixture
def sample_bgr():
    img = cv2.imread(os.path.join(DATA, "astronaut_nasa.png"))
    assert img is not None
    return img


@pytest.fixture
def blank_bgr():
    return np.full((400, 400, 3), 128, np.uint8)


@pytest.fixture(autouse=True)
def temp_results(tmp_path, monkeypatch):
    # never write into the real results/results.csv during tests
    monkeypatch.setattr(storage, "RESULTS_DIR", str(tmp_path))
    monkeypatch.setattr(storage, "RESULTS_CSV", str(tmp_path / "results.csv"))
    return tmp_path / "results.csv"


@pytest.fixture
def live_mode(monkeypatch):
    monkeypatch.setattr(controller, "load_config", lambda: dict(LIVE_CONFIG))


@pytest.fixture
def demo_mode(monkeypatch):
    monkeypatch.setattr(controller, "load_config", lambda: dict(LIVE_CONFIG, demo_mode=True))


def to_jpg_bytes(img):
    ok, buf = cv2.imencode(".jpg", img)
    assert ok
    return buf.tobytes()
