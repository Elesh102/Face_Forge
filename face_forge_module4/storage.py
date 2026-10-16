"""
storage.py — Storage Engine for Face Forge Module 4
===================================================

Handles thread-safe reading and append-only writing of prediction records
to `results/results.csv`.

COLUMNS:
timestamp, source, file_name, frame_number, face_id, emotion, confidence, status, data_source
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
CSV_PATH = os.path.join(RESULTS_DIR, "results.csv")

CSV_HEADER = [
    "timestamp",
    "source",
    "file_name",
    "frame_number",
    "face_id",
    "emotion",
    "confidence",
    "status",
    "data_source"
]


def init_storage():
    """Ensure the results directory and results.csv file with headers exist."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)


def append_record(
    source: str,
    file_name: str,
    frame_number: int,
    face_id: int,
    emotion: str,
    confidence: float,
    status: str,
    data_source: str = "demo",
    timestamp: Optional[str] = None
) -> Dict[str, Any]:
    """
    Append a single prediction record to results.csv.

    Args:
        source: 'image', 'video', or 'webcam'
        file_name: Name of the processed file or 'live_webcam'
        frame_number: 0 for images, integer for video/webcam frame
        face_id: ID/Index of detected face in the frame
        emotion: Dominant emotion label
        confidence: Confidence score float (0.0 to 1.0)
        status: 'Happy', 'Neutral', 'Needs attention', or 'Uncertain'
        data_source: 'demo' or 'live'
        timestamp: Optional ISO/readable timestamp string

    Returns:
        Dict of the saved row.
    """
    init_storage()
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        timestamp,
        source.lower().strip(),
        file_name,
        int(frame_number),
        int(face_id),
        emotion.lower().strip(),
        round(float(confidence), 4),
        status,
        data_source.lower().strip()
    ]

    with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    return dict(zip(CSV_HEADER, row))


def read_all_records() -> List[Dict[str, Any]]:
    """Read all records from results.csv into a list of dicts."""
    init_storage()
    records = []
    if not os.path.exists(CSV_PATH):
        return records

    try:
        with open(CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    except Exception as e:
        print(f"Error reading {CSV_PATH}: {e}")

    return records


def filter_records(
    source: Optional[str] = None,
    emotion: Optional[str] = None,
    date_filter: Optional[str] = None,
    data_source: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter results by source, emotion, date, or data_source.
    """
    rows = read_all_records()
    filtered = []

    for r in rows:
        if source and source.lower() != "all":
            if r.get("source", "").lower() != source.lower():
                continue

        if emotion and emotion.lower() != "all":
            if r.get("emotion", "").lower() != emotion.lower():
                continue

        if data_source and data_source.lower() != "all":
            if r.get("data_source", "").lower() != data_source.lower():
                continue

        if date_filter:
            # Match date prefix YYYY-MM-DD
            ts = r.get("timestamp", "")
            if not ts.startswith(date_filter):
                continue

        filtered.append(r)

    return filtered


def clear_results() -> bool:
    """Clear all records from results.csv, preserving the header."""
    init_storage()
    try:
        with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
        return True
    except Exception as e:
        print(f"Error clearing {CSV_PATH}: {e}")
        return False
