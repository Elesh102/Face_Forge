"""
Face Forge - Adapter for Module 1: Preprocessing & Data Pipeline
File: adapter_preprocess.py

CONTRACT:
    Input:  img (NumPy ndarray, BGR format from OpenCV)
    Output: img (NumPy ndarray, BGR format, preprocessed/normalized)

MOCK BEHAVIOR (TODAY):
    Returns the image unchanged without modification.

HOW TO PLUG IN THE REAL MODULE:
    1. Place teammate's module file (e.g. `module1_preprocess.py`) in this directory.
    2. Import their function inside `preprocess()` below.
    3. Pass `img` to their function, convert their return value to BGR ndarray if needed.
    4. Enable `use_module1: true` in `config.yaml` or through the Settings UI.
"""

import numpy as np

def preprocess(img: np.ndarray, use_real: bool = False) -> np.ndarray:
    """
    Preprocesses an input image (e.g. histogram equalization, resizing, noise reduction).
    
    Args:
        img: np.ndarray in BGR color format.
        use_real: bool flag indicating if real Module 1 should be invoked.
        
    Returns:
        np.ndarray: preprocessed image (BGR).
    """
    if use_real:
        try:
            # Teammate plug-in point:
            # from module1_preprocess import preprocess_image
            # return preprocess_image(img)
            raise NotImplementedError("Module 1 implementation not yet supplied by teammate.")
        except Exception as e:
            print(f"[Warning] Module 1 Preprocessing unavailable: {e}. Falling back to mock (unchanged).")
            return img

    # Mock behavior: return image unchanged
    return img
