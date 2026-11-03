# Tests for evaluation.py - uses made-up prediction rows so the answers can be checked by hand
import pytest

from module3.evaluation import compute_metrics, load_csv, map_labels, parse_label_map


def row(true, pred, status="ok"):
    return {"true_label": true, "predicted": pred if status == "ok" else "",
            "status": status, "correct": (pred == true) if status == "ok" else ""}


def test_label_map_from_text():
    assert parse_label_map(" Surprised = surprise ,0=angry") == {"surprised": "surprise", "0": "angry"}


def test_map_labels_lowercases_and_maps():
    samples = [("a.png", "Happy"), ("b.png", "joy")]
    mapped, skipped = map_labels(samples, {"joy": "happy"}, skip_unknown=False)
    assert [m[2] for m in mapped] == ["happy", "happy"]
    assert not skipped


def test_unknown_label_stops_with_error():
    with pytest.raises(ValueError, match="contempt"):
        map_labels([("a.png", "contempt")], {}, skip_unknown=False)


def test_unknown_label_can_be_skipped():
    mapped, skipped = map_labels([("a.png", "contempt"), ("b.png", "sad")], {}, skip_unknown=True)
    assert len(mapped) == 1 and skipped == {"contempt": 1}


def test_csv_relative_paths(tmp_path):
    csv_file = tmp_path / "labels.csv"
    csv_file.write_text("image_path,true_label\nimgs/a.png,happy\n", encoding="utf-8")
    [(path, label)] = load_csv(str(csv_file))
    assert path == str(tmp_path / "imgs/a.png") and label == "happy"


def test_csv_wrong_columns(tmp_path):
    csv_file = tmp_path / "labels.csv"
    csv_file.write_text("file,label\na.png,happy\n", encoding="utf-8")
    with pytest.raises(ValueError, match="image_path,true_label"):
        load_csv(str(csv_file))


def test_metrics_by_hand():
    # 3 happy -> happy, 1 sad -> happy, 1 neutral -> no face
    rows = [row("happy", "happy")] * 3 + [row("sad", "happy"), row("neutral", None, "no_face")]
    m = compute_metrics(rows)
    assert m["n_total"] == 5 and m["n_predicted"] == 4
    assert m["accuracy_on_predicted"] == pytest.approx(3 / 4)
    assert m["accuracy_end_to_end"] == pytest.approx(3 / 5)
    p, r, f, s = m["per_class"]["happy"]
    assert (p, r, s) == (pytest.approx(0.75), pytest.approx(1.0), 3)
    assert m["present_classes"] == ["happy", "sad"]
    assert m["classes_never_predicted"] == ["neutral"]
    assert m["macro"][0] == pytest.approx((0.75 + 0) / 2)       # precision
    assert m["weighted"][1] == pytest.approx((1.0 * 3 + 0 * 1) / 4)  # recall
    assert m["top_confusions"] == [(1, "sad", "happy")]
    assert m["confusion_matrix"].sum() == 4


def test_metrics_when_nothing_predicted():
    m = compute_metrics([row("happy", None, "no_face")])
    assert m["n_predicted"] == 0 and "accuracy_on_predicted" not in m
