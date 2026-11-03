# Tests for fer2013_to_folder.py - uses a tiny fake fer2013.csv (4 rows)
import cv2
import numpy as np
import pytest

from module3.fer2013_to_folder import FER2013_LABELS, convert


def pixels(value):
    return " ".join([str(value)] * 48 * 48)


@pytest.fixture
def fake_csv(tmp_path):
    path = tmp_path / "fer2013.csv"
    path.write_text(
        "emotion,pixels,Usage\n"
        f"3,{pixels(10)},Training\n"
        f"3,{pixels(20)},PrivateTest\n"
        f"0,{pixels(30)},PrivateTest\n"
        f"6,{pixels(40)},PublicTest\n",
        encoding="utf-8")
    return path


def test_label_order_matches_model():
    # FER-2013 numbers -> names, same order as the fer model uses
    assert FER2013_LABELS == {0: "angry", 1: "disgust", 2: "fear", 3: "happy",
                              4: "sad", 5: "surprise", 6: "neutral"}


def test_only_chosen_usage_is_exported(fake_csv, tmp_path):
    out = tmp_path / "out"
    counts = convert(str(fake_csv), "PrivateTest", str(out))
    assert counts == {"happy": 1, "angry": 1}
    assert sorted(p.name for p in out.iterdir()) == ["angry", "happy"]


def test_image_is_48x48_with_same_pixels(fake_csv, tmp_path):
    out = tmp_path / "out"
    convert(str(fake_csv), "PrivateTest", str(out))
    [png] = list((out / "happy").glob("*.png"))
    img = cv2.imread(str(png), cv2.IMREAD_GRAYSCALE)
    assert img.shape == (48, 48)
    assert np.all(img == 20)  # row 2 of the csv


def test_file_name_keeps_csv_row_number(fake_csv, tmp_path):
    out = tmp_path / "out"
    convert(str(fake_csv), "PrivateTest", str(out))
    assert [p.name for p in (out / "angry").glob("*.png")] == ["row00002.png"]


def test_bad_pixel_count_raises(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("emotion,pixels,Usage\n3,1 2 3,PrivateTest\n", encoding="utf-8")
    with pytest.raises(ValueError, match="2304"):
        convert(str(bad), "PrivateTest", str(tmp_path / "out"))


@pytest.mark.parametrize("emotion", ["9", "-1", "happy"])
def test_bad_emotion_number_raises(tmp_path, emotion):
    bad = tmp_path / "bad.csv"
    bad.write_text(f"emotion,pixels,Usage\n{emotion},{pixels(5)},PrivateTest\n", encoding="utf-8")
    with pytest.raises(ValueError, match="emotion"):
        convert(str(bad), "PrivateTest", str(tmp_path / "out"))


def test_unknown_usage_raises(fake_csv, tmp_path):
    with pytest.raises(ValueError, match="Usage"):
        convert(str(fake_csv), "Testing", str(tmp_path / "out"))


def test_missing_columns_raise(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("label,image\n3,abc\n", encoding="utf-8")
    with pytest.raises(ValueError, match="emotion,pixels,Usage"):
        convert(str(bad), "PrivateTest", str(tmp_path / "out"))
