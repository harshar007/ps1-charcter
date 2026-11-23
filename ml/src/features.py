"""
Feature extraction module for the RetroMorph AI Image Readiness Classifier.
Extracts computer vision and statistical metrics from an uploaded image.
"""

from typing import Dict, Any, Union
import numpy as np
import cv2
from PIL import Image


FEATURE_NAMES = [
    "width",
    "height",
    "aspect_ratio",
    "resolution_mp",
    "brightness_mean",
    "brightness_std",
    "contrast_rms",
    "blur_score",
    "edge_density",
    "color_variance",
    "subject_framing_score",
]


def extract_image_features(image_input: Union[str, np.ndarray, Image.Image]) -> Dict[str, float]:
    """
    Extracts computer vision quality features from an image.
    
    Args:
        image_input: File path, numpy array (BGR/RGB), or PIL Image.
        
    Returns:
        Dict mapping feature name to numeric value.
    """
    if isinstance(image_input, str):
        # Read with OpenCV
        bgr = cv2.imread(image_input)
        if bgr is None:
            # Fallback to PIL
            pil_img = Image.open(image_input).convert("RGB")
            rgb = np.array(pil_img)
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    elif isinstance(image_input, Image.Image):
        rgb = np.array(image_input.convert("RGB"))
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    elif isinstance(image_input, np.ndarray):
        bgr = image_input.copy()
        if len(bgr.shape) == 2:
            bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)
        elif bgr.shape[2] == 4:
            bgr = cv2.cvtColor(bgr, cv2.COLOR_BGRA2BGR)
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    height, width = bgr.shape[:2]
    aspect_ratio = float(width) / float(max(height, 1))
    resolution_mp = float(width * height) / 1_000_000.0

    # Convert to grayscale
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # 1. Brightness statistics
    brightness_mean = float(np.mean(gray))
    brightness_std = float(np.std(gray))

    # 2. Contrast (RMS contrast)
    contrast_rms = float(np.sqrt(np.mean((gray - brightness_mean) ** 2)))

    # 3. Blur score (Variance of Laplacian)
    # Higher = sharper; lower = blurry. Typically < 100 indicates blur
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    blur_score = float(laplacian.var())

    # 4. Edge density via Canny
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.count_nonzero(edges)) / float(max(height * width, 1))

    # 5. Color variance across channels (R, G, B standard deviations)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    ch_stds = [np.std(rgb[:, :, c]) for c in range(3)]
    color_variance = float(np.mean(ch_stds))

    # 6. Subject framing score: Ratio of edge detail in center crop (50% inner area) vs border
    h_start, h_end = int(height * 0.2), int(height * 0.8)
    w_start, w_end = int(width * 0.2), int(width * 0.8)
    center_edges = edges[h_start:h_end, w_start:w_end]
    center_edge_density = float(np.count_nonzero(center_edges)) / float(max(center_edges.size, 1))
    subject_framing_score = float(center_edge_density / (edge_density + 1e-5))

    return {
        "width": float(width),
        "height": float(height),
        "aspect_ratio": round(aspect_ratio, 4),
        "resolution_mp": round(resolution_mp, 4),
        "brightness_mean": round(brightness_mean, 2),
        "brightness_std": round(brightness_std, 2),
        "contrast_rms": round(contrast_rms, 2),
        "blur_score": round(blur_score, 2),
        "edge_density": round(edge_density, 5),
        "color_variance": round(color_variance, 2),
        "subject_framing_score": round(subject_framing_score, 3),
    }


def analyze_image_quality_rules(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Returns rule-based diagnostic flags and retake suggestions based on features.
    Used alongside the ML model to give users actionable feedback.
    """
    issues = []
    tips = []

    if features["resolution_mp"] < 0.15:
        issues.append("Image resolution is very low (less than 0.15 MP).")
        tips.append("Upload an image of at least 512×512 resolution for sharp character details.")

    if features["blur_score"] < 75.0:
        issues.append("Image appears blurry or out of focus.")
        tips.append("Hold the camera steady or use better lighting to prevent motion blur.")

    if features["brightness_mean"] < 45.0:
        issues.append("Image is underexposed / too dark.")
        tips.append("Ensure adequate frontal lighting so facial features are visible.")
    elif features["brightness_mean"] > 220.0:
        issues.append("Image is overexposed / washed out.")
        tips.append("Reduce harsh backlighting or glare.")

    if features["contrast_rms"] < 25.0:
        issues.append("Image has very low contrast.")
        tips.append("Avoid flat gray lighting; distinct clothing and face contours help 3D reconstruction.")

    if features["aspect_ratio"] > 2.2 or features["aspect_ratio"] < 0.4:
        issues.append("Unusual aspect ratio (extreme panorama or narrow sliver).")
        tips.append("Use standard portrait (3:4, 4:5) or square (1:1) framing.")

    return {
        "is_acceptable": len(issues) == 0,
        "issues": issues,
        "tips": tips,
    }
