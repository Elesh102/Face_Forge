"""
adapter_preprocess.py — Adapter for Module 1: Dataset and Preprocessing
========================================================================

ROLE IN FACE FORGE:
Acts as the integration bridge between Module 4 (UI/Integration) and Module 1
(Image and frame preprocessing: contrast adjustment, lighting normalization,
and image resizing).

HOW TO REPLACE THIS MOCK WITH REAL TEAMMATE CODE:
1. Place Teammate 1's Python file (e.g. `preprocess_module.py`) into the project root or adapters folder.
2. In this file, import their preprocessing function:
       from preprocess_module import process_image
3. In `preprocess(img, config=None)`, replace the return statement with:
       return process_image(img)
4. Enable `use_module1: true` in `config.yaml` or through the Settings page.
5. If the import fails or an exception is raised during preprocessing, this adapter
   automatically catches it, logs a warning, and returns the image unchanged so the system never crashes.
"""

import logging
import numpy as np

logger = logging.getLogger(__name__)

# State tracking for UI notifications
MODULE1_WARNING = None


def preprocess(img: np.ndarray, config: dict = None) -> np.ndarray:
    """
    Preprocess an input image or video frame.

    Args:
        img: np.ndarray (OpenCV BGR or RGB image)
        config: Optional dict containing configuration settings.

    Returns:
        np.ndarray: Preprocessed image.
    """
    global MODULE1_WARNING
    MODULE1_WARNING = None

    use_real = config.get("use_module1", False) if config else False

    if use_real:
        try:
            # TEAMMATE INTEGRATION POINT (Module 1):
            # from teammate_module1 import preprocess_image
            # return preprocess_image(img)
            raise ImportError("Teammate's Module 1 file not detected in project.")
        except Exception as e:
            MODULE1_WARNING = f"Module 1 real adapter unavailable ({str(e)}). Falling back to mock preprocessing."
            logger.warning(MODULE1_WARNING)

    # Mock implementation: returns the image unchanged
    return img


def get_warning():
    """Returns the latest warning string if Module 1 failed to load, else None."""
    return MODULE1_WARNING
