# First test of the fer library on one image, to see what it really returns.
#   python module3\smoke_test_fer.py
#   python module3\smoke_test_fer.py path\to\face.jpg

import os
import sys

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import cv2
import tensorflow as tf
import fer
from fer.fer import FER

image_path = os.path.join(os.path.dirname(__file__), "sample_inputs", "astronaut_nasa.png")
if len(sys.argv) > 1:
    image_path = sys.argv[1]

print("python    :", sys.version.split()[0])
print("fer       :", fer.__version__)
print("tensorflow:", tf.__version__)
print("opencv    :", cv2.__version__)
print("image     :", image_path)

img = cv2.imread(image_path)
if img is None:
    print("ERROR: could not read image")
    sys.exit(1)
print("shape     :", img.shape)

# 1. default model (TFLite)
print("\n--- fer default (Haar face detector + TFLite model) ---")
detector = FER()
result = detector.detect_emotions(img)
print(result)
for face in result:
    scores = face["emotions"]
    print("box     :", face["box"])
    print("dominant:", max(scores, key=scores.get))
    print("sum     :", round(sum(scores.values()), 4))

# 2. full keras model, to compare
print("\n--- fer keras model (use_tflite=False) ---")
detector2 = FER(use_tflite=False)
print(detector2.detect_emotions(img))

# 3. check the last layer - softmax means the scores add up to 1
model = detector2._FER__emotion_classifier
print("\n--- model ---")
print("input :", model.input_shape)
print("output:", model.output_shape)
print("last layer activation:", model.layers[-1].activation)
