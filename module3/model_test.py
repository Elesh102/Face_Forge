# Module 3 - run the detector on all images in a folder and save the predictions.
# The sample images have no labels, so this only checks that it works and how fast.
# It does NOT give accuracy (use evaluation.py for that).
#
#   python module3\model_test.py
#   python module3\model_test.py --folder some\folder --crop

import argparse
import csv
import os
import platform
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module3.emotion_detector import EMOTIONS, EmotionDetector, load_bgr_image

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE_TYPES = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default=os.path.join(HERE, "sample_inputs"))
    parser.add_argument("--out", default=os.path.join(HERE, "reports", "sample_predictions.csv"))
    parser.add_argument("--crop", action="store_true", help="images are already face crops")
    args = parser.parse_args()

    images = sorted(f for f in os.listdir(args.folder) if f.lower().endswith(IMAGE_TYPES))
    if not images:
        print("no images found in", args.folder)
        sys.exit(1)

    detector = EmotionDetector()
    predict = detector.predict_face_crop if args.crop else detector.predict

    # first call is slow (tensorflow starting), so run it once before timing
    predict(load_bgr_image(os.path.join(args.folder, images[0])))

    rows = []
    times = []
    for name in images:
        try:
            img = load_bgr_image(os.path.join(args.folder, name))
        except ValueError as e:
            print(f"{name}: {e}")
            rows.append({"image": name, "status": "error", "error": str(e)})
            continue

        start = time.perf_counter()
        result = predict(img)
        ms = (time.perf_counter() - start) * 1000
        times.append(ms)

        if result["status"] != "ok":
            print(f"{name}: {result['status']} ({ms:.1f} ms)")
            rows.append({"image": name, "status": result["status"], "error": result["error"],
                         "time_ms": round(ms, 1)})
            continue

        for i, face in enumerate(result["faces"]):
            print(f"{name}: face {i} = {face['dominant_emotion']} {face['score']:.2f} "
                  f"box={face['box']} ({ms:.1f} ms)")
            row = {"image": name, "face_index": i, "status": "ok",
                   "box": " ".join(str(v) for v in face["box"]),
                   "dominant_emotion": face["dominant_emotion"], "score": face["score"],
                   "time_ms": round(ms, 1)}
            row.update(face["scores"])
            rows.append(row)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    columns = ["image", "face_index", "status", "error", "box", "dominant_emotion", "score",
               *EMOTIONS, "time_ms"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print("images :", len(images), "(face crop mode)" if args.crop else "")
    print("model  :", detector.model_info)
    print("machine:", platform.processor(), "| Python", platform.python_version())
    if times:
        print(f"time   : avg {sum(times) / len(times):.1f} ms per image "
              f"(min {min(times):.1f}, max {max(times):.1f})")
    print("saved  :", args.out)
    print("note   : no labels here, so this is not accuracy")


if __name__ == "__main__":
    main()
