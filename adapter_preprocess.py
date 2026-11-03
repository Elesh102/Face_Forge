"""
=============================================================================
FaceForge - Adapter for Module 1: Preprocessing & Data Pipeline
File: adapter_preprocess.py
Coordinated by: Member 4 (Integration) for Member 1 (Preprocessing)
Group G2 (IT) - B.Tech Final Year Project - SKIT Jaipur

Purpose:
Connects Member 1's preprocessing functions (module1_preprocess.py)
to the main FaceForge processing pipeline cleanly.
=============================================================================
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
            # Member 1 (Dataset & Preprocessing) Live Integration
            from module1_preprocess import preprocess_image
            return preprocess_image(img)
        except Exception as e:
            print(f"[Warning] Module 1 Preprocessing unavailable: {e}. Falling back to unchanged frame.")
            return img

    # Mock behavior: return image unchanged
    return img
