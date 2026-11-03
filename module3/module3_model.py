# Function asked for by Module 4 (Face Forge integration guide):
#   predict_emotion(face_crop) -> dict with the 7 emotion scores
#   run_inference(face_crop)   -> same function, name from Module 4's newer spec
# If the prediction fails it raises ValueError instead of returning fake scores.

from module3.emotion_detector import EmotionDetector

detector = None


def predict_emotion(face_crop):
    global detector
    if detector is None:
        detector = EmotionDetector()  # load model on first call only

    result = detector.predict_face_crop(face_crop)
    if result["status"] != "ok":
        raise ValueError(f"Module 3 could not predict an emotion: {result['error']}")
    return result["faces"][0]["scores"]


# Module 4's newer spec uses this name for the same function
run_inference = predict_emotion
