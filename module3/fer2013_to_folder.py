# Convert the FER-2013 csv (from Kaggle, used by Module 1) into image folders
# that evaluation.py can read:   out_dir\happy\row00012.png, out_dir\sad\...
#
#   python module3\fer2013_to_folder.py fer2013.csv --usage PrivateTest --out data\fer2013_private
#
# fer2013.csv columns: emotion (0-6), pixels (2304 numbers = 48x48 gray), Usage
# Usage is Training / PublicTest / PrivateTest. The fer model was trained on the
# Training rows, so evaluate on PrivateTest.

import argparse
import csv
import os

import cv2
import numpy as np

# label numbers used by FER-2013 (same order as the fer model)
FER2013_LABELS = {0: "angry", 1: "disgust", 2: "fear", 3: "happy",
                  4: "sad", 5: "surprise", 6: "neutral"}
USAGES = ["Training", "PublicTest", "PrivateTest"]


def convert(csv_path, usage, out_dir):
    if usage not in USAGES:
        raise ValueError(f"Usage must be one of {USAGES}, got '{usage}'")

    counts = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not {"emotion", "pixels", "Usage"} <= set(reader.fieldnames or []):
            raise ValueError(f"csv must have columns emotion,pixels,Usage, found {reader.fieldnames}")

        for i, row in enumerate(reader):
            if row["Usage"] != usage:
                continue
            values = row["pixels"].split()
            if len(values) != 48 * 48:
                raise ValueError(f"row {i}: expected 2304 pixels (48x48), got {len(values)}")
            if row["emotion"].strip() not in [str(k) for k in FER2013_LABELS]:
                raise ValueError(f"row {i}: emotion must be 0-6, got '{row['emotion']}'")
            label = FER2013_LABELS[int(row["emotion"])]
            img = np.array(values, dtype=np.uint8).reshape(48, 48)

            folder = os.path.join(out_dir, label)
            os.makedirs(folder, exist_ok=True)
            cv2.imwrite(os.path.join(folder, f"row{i:05d}.png"), img)
            counts[label] = counts.get(label, 0) + 1
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    parser.add_argument("--usage", default="PrivateTest")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    counts = convert(args.csv, args.usage, args.out)
    print(f"saved {sum(counts.values())} images to {args.out}")
    for label in FER2013_LABELS.values():
        print(f"  {label:9s} {counts.get(label, 0)}")
