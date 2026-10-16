"""
analytics.py — Statistical Computation and Chart Generator for Face Forge Module 4
===================================================================================

Uses pandas and matplotlib to compute aggregates from results/results.csv:
  - Total records / frames processed
  - Most frequent (dominant) detected expression
  - Average confidence
  - 7-class emotion distribution
  - Temporal distribution
  - Chart generation (base64 PNG encoded)
"""

import os
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server environments
import matplotlib.pyplot as plt

import storage
from adapters.adapter_emotion import EMOTION_CLASSES


def get_analytics(data_source: str = "all") -> dict:
    """
    Compute key metrics and chart representations from results.csv.

    Args:
        data_source: 'all', 'demo', or 'live'

    Returns:
        Dict with metrics, distribution counts, and base64 chart images.
    """
    records = storage.read_all_records()

    if not records:
        return {
            "empty": True,
            "message": "No prediction records logged yet. Run detection on an image, video, or webcam to generate analytics.",
            "total_records": 0,
            "dominant_emotion": "None",
            "average_confidence": 0.0,
            "distribution": {emo: 0 for emo in EMOTION_CLASSES},
            "chart_distribution": None,
            "chart_timeline": None
        }

    df = pd.DataFrame(records)

    # Filter by data_source if requested
    if data_source and data_source.lower() != "all":
        if "data_source" in df.columns:
            df = df[df["data_source"].str.lower() == data_source.lower()]

    if df.empty:
        return {
            "empty": True,
            "message": f"No records found for filter tier '{data_source}'.",
            "total_records": 0,
            "dominant_emotion": "None",
            "average_confidence": 0.0,
            "distribution": {emo: 0 for emo in EMOTION_CLASSES},
            "chart_distribution": None,
            "chart_timeline": None
        }

    # Ensure numeric types
    if "confidence" in df.columns:
        df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.0)

    total_records = len(df)

    # Dominant emotion
    dominant_emotion = "None"
    if "emotion" in df.columns and not df["emotion"].empty:
        mode_series = df["emotion"].mode()
        if not mode_series.empty:
            dominant_emotion = str(mode_series.iloc[0]).capitalize()

    # Average confidence
    avg_conf = 0.0
    if "confidence" in df.columns:
        avg_conf = round(float(df["confidence"].mean()), 4)

    # 7-class distribution counts
    counts = {emo: 0 for emo in EMOTION_CLASSES}
    if "emotion" in df.columns:
        raw_counts = df["emotion"].str.lower().value_counts().to_dict()
        for emo, count in raw_counts.items():
            if emo in counts:
                counts[emo] = int(count)

    # Generate charts
    chart_distribution = _generate_distribution_chart(counts)
    chart_timeline = _generate_timeline_chart(df)

    return {
        "empty": False,
        "message": None,
        "total_records": total_records,
        "dominant_emotion": dominant_emotion,
        "average_confidence": avg_conf,
        "distribution": counts,
        "chart_distribution": chart_distribution,
        "chart_timeline": chart_timeline
    }


def _generate_distribution_chart(counts: dict) -> str:
    """Generate a clean matplotlib bar chart of emotion frequencies."""
    emotions = list(counts.keys())
    values = list(counts.values())

    plt.figure(figsize=(7, 3.8), facecolor="#0f172a")
    ax = plt.subplot(111)
    ax.set_facecolor("#0f172a")

    # High-contrast, clean color palette
    bar_colors = ["#f87171", "#2dd4bf", "#c084fc", "#34d399", "#60a5fa", "#fbbf24", "#94a3b8"]

    bars = ax.bar(emotions, values, color=bar_colors, edgecolor="none", width=0.6)

    # Styling
    ax.set_title("Detected Expression Distribution", color="#f8fafc", fontsize=12, pad=12, fontweight="bold")
    ax.tick_params(axis="x", colors="#cbd5e1", labelsize=9)
    ax.tick_params(axis="y", colors="#cbd5e1", labelsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.15, color="#ffffff")

    for spine in ax.spines.values():
        spine.set_edgecolor("#334155")

    # Add count labels above bars
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.annotate(
                f"{height}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom",
                color="#ffffff", fontsize=8, fontweight="bold"
            )

    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=130, facecolor=plt.gcf().get_facecolor(), edgecolor="none")
    plt.close()

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def _generate_timeline_chart(df: pd.DataFrame) -> str:
    """Generate a chronological timeline chart showing detected confidence and emotion trends."""
    if df.empty or "timestamp" not in df.columns:
        return None

    try:
        sample_df = df.tail(30).copy()  # Last 30 predictions
        sample_df["ts"] = pd.to_datetime(sample_df["timestamp"], errors="coerce")
        sample_df = sample_df.dropna(subset=["ts"]).sort_values("ts")

        if len(sample_df) < 2:
            return None

        plt.figure(figsize=(7, 3.8), facecolor="#0f172a")
        ax = plt.subplot(111)
        ax.set_facecolor("#0f172a")

        x_indices = range(len(sample_df))
        y_conf = sample_df["confidence"].values

        ax.plot(x_indices, y_conf, color="#38bdf8", marker="o", markersize=4, linewidth=2, label="Confidence")
        ax.fill_between(x_indices, y_conf, color="#38bdf8", alpha=0.15)

        ax.set_title("Expression Confidence Timeline (Recent Detections)", color="#f8fafc", fontsize=12, pad=12, fontweight="bold")
        ax.set_ylabel("Confidence", color="#cbd5e1", fontsize=9)
        ax.tick_params(axis="x", colors="#cbd5e1", labelsize=8)
        ax.tick_params(axis="y", colors="#cbd5e1", labelsize=9)
        ax.set_ylim(0.0, 1.05)
        ax.grid(True, linestyle="--", alpha=0.15, color="#ffffff")

        for spine in ax.spines.values():
            spine.set_edgecolor("#334155")

        plt.tight_layout()
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=130, facecolor=plt.gcf().get_facecolor(), edgecolor="none")
        plt.close()

        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Error generating timeline chart: {e}")
        return None
