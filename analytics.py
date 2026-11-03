"""
=============================================================================
FaceForge - Module 4: Analytics Engine (analytics.py)
Contributed by: Member 4 (System Integration, UI, Storage & Analytics)
Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur

Responsibilities of Member 4:
- Computes emotion distribution counts and percentages from results.csv
- Calculates average model confidence across emotions
- Aggregates timeline trends and identifies most frequent expression
- Provides formatted analytics data for React charts (Recharts)
=============================================================================
"""

from typing import Dict, Any, List, Optional
import os
import pandas as pd
import numpy as np

ALL_EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

def compute_analytics(
    df: pd.DataFrame,
    data_source_filter: str = "all"
) -> Dict[str, Any]:
    """
    Computes comprehensive analytics from the results DataFrame.
    
    Args:
        df: pandas DataFrame from storage.load_results()
        data_source_filter: 'all', 'demo', or 'live'
        
    Returns:
        Dict containing summary metrics, distributions, and timeline points.
    """
    # Empty default structure
    default_response = {
        "total_records": 0,
        "total_frames": 0,
        "most_frequent_emotion": "None",
        "average_confidence": 0.0,
        "emotion_distribution": {emo: {"count": 0, "percentage": 0.0} for emo in ALL_EMOTIONS},
        "status_distribution": {
            "Happy": {"count": 0, "percentage": 0.0},
            "Neutral": {"count": 0, "percentage": 0.0},
            "Needs attention": {"count": 0, "percentage": 0.0},
            "Uncertain": {"count": 0, "percentage": 0.0}
        },
        "timeline": [],
        "has_data": False
    }

    if df.empty:
        return default_response

    # Apply filter if specified
    filtered = df.copy()
    if data_source_filter in ["demo", "live"]:
        filtered = filtered[filtered["data_source"].str.lower() == data_source_filter.lower()]

    if filtered.empty:
        return default_response

    total_records = len(filtered)
    # Estimate total frames by unique combination of file_name and frame_number
    total_frames = filtered.groupby(["file_name", "frame_number"]).ngroups if ("file_name" in filtered.columns and "frame_number" in filtered.columns) else total_records

    # Confidence
    conf_series = pd.to_numeric(filtered["confidence"], errors="coerce").dropna()
    avg_conf = float(conf_series.mean()) if not conf_series.empty else 0.0

    # Emotion counts and percentages
    emotion_counts = filtered["emotion"].str.lower().value_counts()
    most_frequent = str(emotion_counts.index[0]).capitalize() if not emotion_counts.empty else "None"

    emotion_dist = {}
    for emo in ALL_EMOTIONS:
        cnt = int(emotion_counts.get(emo, 0))
        pct = round((cnt / total_records) * 100, 1) if total_records > 0 else 0.0
        emotion_dist[emo] = {"count": cnt, "percentage": pct}

    # Status counts and percentages
    status_counts = filtered["status"].value_counts()
    status_dist = {}
    for st in ["Happy", "Neutral", "Needs attention", "Uncertain"]:
        cnt = int(status_counts.get(st, 0))
        pct = round((cnt / total_records) * 100, 1) if total_records > 0 else 0.0
        status_dist[st] = {"count": cnt, "percentage": pct}

    # Timeline (group by timestamp or frame sequence, sample top 50 recent points)
    timeline_records = []
    # Sort chronologically if timestamp exists
    sorted_df = filtered.copy()
    if "timestamp" in sorted_df.columns:
        sorted_df["timestamp_dt"] = pd.to_datetime(sorted_df["timestamp"], errors="coerce")
        sorted_df = sorted_df.sort_values(by="timestamp_dt")

    recent_slice = sorted_df.tail(60)
    for idx, row in recent_slice.iterrows():
        timeline_records.append({
            "timestamp": str(row.get("timestamp", "")),
            "frame": int(row.get("frame_number", 0)),
            "emotion": str(row.get("emotion", "neutral")),
            "confidence": round(float(row.get("confidence", 0.0)), 2),
            "source": str(row.get("source", "image")),
            "data_source": str(row.get("data_source", "demo"))
        })

    return {
        "total_records": total_records,
        "total_frames": total_frames,
        "most_frequent_emotion": most_frequent,
        "average_confidence": round(avg_conf, 4),
        "emotion_distribution": emotion_dist,
        "status_distribution": status_dist,
        "timeline": timeline_records,
        "has_data": True
    }

def generate_matplotlib_charts(df: pd.DataFrame, output_dir: str) -> Optional[str]:
    """
    Generates a matplotlib emotion distribution plot for export or report viva.
    """
    if df.empty:
        return None
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        os.makedirs(output_dir, exist_ok=True)
        chart_path = os.path.join(output_dir, "emotion_distribution.png")

        counts = df["emotion"].str.lower().value_counts()
        labels = [e for e in ALL_EMOTIONS if e in counts]
        values = [counts.get(e, 0) for e in labels]

        plt.figure(figsize=(8, 4.5))
        plt.style.use("dark_background")
        colors = ["#f43f5e", "#d97706", "#8b5cf6", "#10b981", "#3b82f6", "#ec4899", "#64748b"]
        plt.bar(labels, values, color=colors[:len(labels)], edgecolor="#334155")
        plt.title("Face Forge - Detected Expression Distribution", fontsize=14, color="#f8fafc")
        plt.xlabel("Expression Category", fontsize=11, color="#94a3b8")
        plt.ylabel("Record Count", fontsize=11, color="#94a3b8")
        plt.grid(axis="y", linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150)
        plt.close()
        return chart_path
    except Exception as e:
        print(f"[Warning] Failed to generate matplotlib chart: {e}")
        return None
