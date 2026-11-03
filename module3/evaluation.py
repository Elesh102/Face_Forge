# Module 3 - evaluate the FER model on labelled test images (from Module 1)
#
# Two ways to give the data:
#   python module3\evaluation.py --csv labels.csv        (columns: image_path,true_label)
#   python module3\evaluation.py --folder test_set       (test_set\happy\*.jpg, test_set\sad\*.jpg ...)
#
# Options:
#   --crop          images are already face crops (like FER-2013), skip face detection
#   --label-map     rename labels, e.g. "surprised=surprise,joy=happy"
#   --skip-unknown  drop labels the model doesn't have (e.g. contempt)
#
# Output in module3/reports: metrics_report.txt, confusion_matrix.png, predictions.csv

import argparse
import csv
import datetime
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from module3.emotion_detector import EMOTIONS, EmotionDetector

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE_TYPES = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def load_csv(csv_path):
    folder = os.path.dirname(os.path.abspath(csv_path))
    samples = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if "image_path" not in reader.fieldnames or "true_label" not in reader.fieldnames:
            raise ValueError(f"CSV must have columns image_path,true_label, found {reader.fieldnames}")
        for row in reader:
            path = os.path.join(folder, row["image_path"].strip())  # works for relative and full paths
            samples.append((os.path.normpath(path), row["true_label"]))
    return samples


def load_folder(root):
    samples = []
    for label in sorted(os.listdir(root)):
        sub = os.path.join(root, label)
        if os.path.isdir(sub):
            for name in sorted(os.listdir(sub)):
                if name.lower().endswith(IMAGE_TYPES):
                    samples.append((os.path.join(sub, name), label))
    return samples


def parse_label_map(text):
    # "a=b,c=d" -> {"a": "b", "c": "d"}
    label_map = {}
    for pair in text.split(","):
        if pair.strip() == "":
            continue
        if "=" not in pair:
            raise ValueError(f"bad --label-map entry '{pair}', use old=new")
        old, new = pair.split("=", 1)
        label_map[old.strip().lower()] = new.strip().lower()
    return label_map


def map_labels(samples, label_map, skip_unknown):
    # convert dataset labels to model labels, stop if a label is unknown
    mapped = []
    unknown = Counter()
    for path, raw in samples:
        label = raw.strip().lower()
        label = label_map.get(label, label)
        if label in EMOTIONS:
            mapped.append((path, raw, label))
        else:
            unknown[raw] += 1
    if unknown and not skip_unknown:
        raise ValueError(f"labels not in the model: {dict(unknown)}. Model classes: {EMOTIONS}. "
                         f"Use --label-map or --skip-unknown")
    return mapped, unknown


def run_predictions(detector, samples, crop):
    rows = []
    for i, (path, raw, true_label) in enumerate(samples, 1):
        if crop:
            result = detector.predict_face_crop(path)
        else:
            result = detector.predict(path)

        row = {"image_path": path, "raw_label": raw, "true_label": true_label,
               "status": result["status"], "error": result["error"] or "",
               "num_faces": result["num_faces"], "predicted": "", "score": "", "correct": ""}
        if result["status"] == "ok":
            # if more than one face is found, use the biggest one
            face = max(result["faces"], key=lambda f: f["box"][2] * f["box"][3])
            row["predicted"] = face["dominant_emotion"]
            row["score"] = face["score"]
            row["correct"] = face["dominant_emotion"] == true_label
            row.update(face["scores"])
        rows.append(row)

        if i % 100 == 0 or i == len(samples):
            print(f"  {i}/{len(samples)} done")
    return rows


def compute_metrics(rows):
    ok = [r for r in rows if r["status"] == "ok"]
    y_true = [r["true_label"] for r in ok]
    y_pred = [r["predicted"] for r in ok]
    true_counts = Counter(r["true_label"] for r in rows)
    present = [e for e in EMOTIONS if e in y_true]  # classes used for macro/weighted avg

    m = {
        "n_total": len(rows),
        "n_predicted": len(ok),
        "failures": Counter(r["status"] for r in rows if r["status"] != "ok"),
        "true_counts": true_counts,
        "present_classes": present,
        # classes where every image failed (no face / error)
        "classes_never_predicted": [e for e in EMOTIONS if true_counts[e] > 0 and e not in present],
    }
    if len(ok) == 0:
        return m

    m["accuracy_on_predicted"] = accuracy_score(y_true, y_pred)
    m["accuracy_end_to_end"] = sum(r["correct"] is True for r in rows) / len(rows)

    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=EMOTIONS, zero_division=0)
    m["per_class"] = {e: (p[i], r[i], f[i], int(s[i])) for i, e in enumerate(EMOTIONS)}
    for avg in ["macro", "weighted"]:
        p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, labels=present,
                                                     average=avg, zero_division=0)
        m[avg] = (p, r, f)

    cm = confusion_matrix(y_true, y_pred, labels=EMOTIONS)
    m["confusion_matrix"] = cm
    mistakes = []
    for i in range(len(EMOTIONS)):
        for j in range(len(EMOTIONS)):
            if i != j and cm[i, j] > 0:
                mistakes.append((int(cm[i, j]), EMOTIONS[i], EMOTIONS[j]))
    m["top_confusions"] = sorted(mistakes, reverse=True)[:5]
    return m


def save_predictions_csv(rows, path):
    columns = ["image_path", "raw_label", "true_label", "status", "predicted", "score",
               "correct", *EMOTIONS, "num_faces", "error"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def save_confusion_matrix(cm, path, title):
    import matplotlib
    matplotlib.use("Agg")  # save to file, don't open a window
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    # colour = % of the true class (row %), so small classes are still visible
    row_sums = cm.sum(axis=1, keepdims=True)
    pct = np.divide(cm, row_sums, out=np.zeros(cm.shape), where=row_sums > 0)
    blues = LinearSegmentedColormap.from_list(
        "blues", ["#f4f8fd", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])

    n = len(EMOTIONS)
    fig, ax = plt.subplots(figsize=(8, 7), dpi=150)
    ax.imshow(pct, cmap=blues, vmin=0, vmax=1)

    for i in range(n):
        for j in range(n):
            if row_sums[i, 0] == 0:
                text, color = "-", "#6b6b6b"
            elif cm[i, j] == 0:
                text, color = "0", "#6b6b6b"
            else:
                text = f"{cm[i, j]}\n{pct[i, j]:.0%}"
                color = "white" if pct[i, j] >= 0.5 else "#1f1f1f"
            ax.text(j, i, text, ha="center", va="center", fontsize=9, color=color)

    # white lines between cells
    ax.set_xticks(np.arange(n + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(n + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="both", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_xticks(range(n), EMOTIONS, rotation=30, ha="right")
    ax.set_yticks(range(n), [f"{e} (n={int(row_sums[i, 0])})" for i, e in enumerate(EMOTIONS)])
    ax.set_xlabel("Predicted emotion")
    ax.set_ylabel("True emotion")
    ax.set_title(title, fontsize=11, loc="left")
    fig.text(0.01, 0.01, "Each cell: count and % of that true class. Diagonal = correct.",
             fontsize=8, color="#6b6b6b")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def write_report(m, args, model_info, label_map, skipped, path):
    lines = []
    add = lines.append
    add("MODULE 3 - EVALUATION REPORT")
    add("=" * 50)
    add(f"date          : {datetime.datetime.now():%Y-%m-%d %H:%M}")
    add(f"dataset       : {args.dataset_name}")
    add(f"source        : {args.csv or args.folder}")
    add(f"input mode    : {'face crops (no face detection)' if args.crop else 'full images (biggest face used)'}")
    add(f"model         : {model_info}")
    add(f"label mapping : {label_map or 'none'}")
    if skipped:
        add(f"skipped       : {dict(skipped)} (labels not in the model)")
    add("")
    add(f"images        : {m['n_total']}")
    add(f"predicted     : {m['n_predicted']}")
    for status, count in m["failures"].items():
        add(f"{status:14s}: {count}")
    add("per class     : " + ", ".join(f"{e}={m['true_counts'].get(e, 0)}" for e in EMOTIONS))

    if m["n_predicted"] == 0:
        add("\nNo predictions, so no metrics.")
    else:
        add("")
        add(f"accuracy (predicted images only) : {m['accuracy_on_predicted']:.4f}")
        add(f"accuracy (all images, failures counted wrong) : {m['accuracy_end_to_end']:.4f}")
        add("")
        add(f"{'class':12s} {'precision':>9s} {'recall':>7s} {'f1':>7s} {'support':>8s}")
        for e in EMOTIONS:
            p, r, f, s = m["per_class"][e]
            add(f"{e:12s} {p:9.4f} {r:7.4f} {f:7.4f} {s:8d}")
        for avg in ["macro", "weighted"]:
            p, r, f = m[avg]
            add(f"{avg + ' avg':12s} {p:9.4f} {r:7.4f} {f:7.4f}")
        add("")
        add("confusion matrix (rows = true, columns = predicted)")
        add(" " * 12 + "".join(f"{e[:8]:>9s}" for e in EMOTIONS))
        for i, e in enumerate(EMOTIONS):
            add(f"{e:12s}" + "".join(f"{v:9d}" for v in m["confusion_matrix"][i]))
        add("")
        add("most common mistakes (true -> predicted):")
        for count, t, p in m["top_confusions"]:
            add(f"  {t} -> {p}: {count}")
        if not m["top_confusions"]:
            add("  none")
        add("")
        add("notes:")
        add(f"- macro avg = simple average over these classes: {m['present_classes']}")
        add("- weighted avg = average weighted by number of images per class")
        if m["classes_never_predicted"]:
            add(f"- left out of averages (all images failed): {m['classes_never_predicted']}")
        add("- model score is a softmax output, not a real probability")
        add("- these results are only for this dataset")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Evaluate FER on labelled images")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv")
    source.add_argument("--folder")
    parser.add_argument("--crop", action="store_true")
    parser.add_argument("--label-map", default="")
    parser.add_argument("--skip-unknown", action="store_true")
    parser.add_argument("--dataset-name", default="unnamed dataset")
    parser.add_argument("--out-dir", default=os.path.join(HERE, "reports"))
    args = parser.parse_args()

    try:
        samples = load_csv(args.csv) if args.csv else load_folder(args.folder)
        label_map = parse_label_map(args.label_map)
        samples, skipped = map_labels(samples, label_map, args.skip_unknown)
    except (OSError, ValueError) as e:
        print("ERROR:", e)
        sys.exit(1)
    if not samples:
        print("ERROR: no labelled images found")
        sys.exit(1)

    print(f"Evaluating {len(samples)} images...")
    detector = EmotionDetector()
    rows = run_predictions(detector, samples, args.crop)
    m = compute_metrics(rows)

    os.makedirs(args.out_dir, exist_ok=True)
    report_path = os.path.join(args.out_dir, "metrics_report.txt")
    save_predictions_csv(rows, os.path.join(args.out_dir, "predictions.csv"))
    write_report(m, args, detector.model_info, label_map, skipped, report_path)
    if m["n_predicted"] > 0:
        title = f"Confusion matrix - {args.dataset_name} ({m['n_predicted']} of {m['n_total']} images)"
        save_confusion_matrix(m["confusion_matrix"], os.path.join(args.out_dir, "confusion_matrix.png"), title)

    print(open(report_path, encoding="utf-8").read())
    print("saved in", args.out_dir)


if __name__ == "__main__":
    main()
