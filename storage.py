"""
Face Forge - Module 4 Storage Layer (storage.py)
Handles append-only persistence of emotion detection results to CSV.
Ensures data integrity even if the application terminates mid-stream.
"""

import os
import csv
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
RESULTS_CSV = os.path.join(RESULTS_DIR, "results.csv")

CSV_COLUMNS = [
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

def init_storage() -> None:
    """Ensure results directory and results.csv exist with header."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    if not os.path.exists(RESULTS_CSV):
        with open(RESULTS_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)

def save_result(
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
    Appends one result record to results.csv with immediate disk flush.
    Ensures that a crash never corrupts previously recorded rows.
    """
    init_storage()
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        timestamp,
        source,
        file_name,
        int(frame_number),
        int(face_id),
        str(emotion).lower(),
        round(float(confidence), 4),
        str(status),
        str(data_source).lower()
    ]

    with open(RESULTS_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)
        f.flush()
        os.fsync(f.fileno())

    return {col: val for col, val in zip(CSV_COLUMNS, row)}

def load_results() -> pd.DataFrame:
    """
    Loads results.csv into a pandas DataFrame.
    Returns an empty DataFrame with the proper columns if file does not exist or is empty.
    """
    init_storage()
    if not os.path.exists(RESULTS_CSV) or os.path.getsize(RESULTS_CSV) == 0:
        return pd.DataFrame(columns=CSV_COLUMNS)
    try:
        df = pd.read_csv(RESULTS_CSV)
        # Ensure column types
        if not df.empty:
            df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.0)
            df["frame_number"] = pd.to_numeric(df["frame_number"], errors="coerce").fillna(0).astype(int)
            df["face_id"] = pd.to_numeric(df["face_id"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        print(f"[Warning] Failed to load results.csv: {e}")
        return pd.DataFrame(columns=CSV_COLUMNS)

def clear_results() -> bool:
    """Clears all records and resets the CSV file with just headers."""
    init_storage()
    try:
        with open(RESULTS_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)
            f.flush()
            os.fsync(f.fileno())
        return True
    except Exception as e:
        print(f"[Error] Failed to clear results: {e}")
        return False
