"""
Unit tests for ML feature extraction, training artifacts, and prediction.
"""

import os
import pytest
import numpy as np
from PIL import Image

import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if os.path.join(PROJECT_ROOT, "ml", "src") not in sys.path:
    sys.path.append(os.path.join(PROJECT_ROOT, "ml", "src"))

from features import extract_image_features, analyze_image_quality_rules, FEATURE_NAMES
from predict import predict_image_quality


def test_feature_extraction():
    # Create test image (512x512 with gradient)
    img_arr = np.zeros((512, 512, 3), dtype=np.uint8)
    img_arr[:, :, 0] = 150
    img_arr[:, :, 1] = 120
    img_arr[:, :, 2] = 90
    test_img = Image.fromarray(img_arr)

    feats = extract_image_features(test_img)
    for name in FEATURE_NAMES:
        assert name in feats, f"Missing feature: {name}"

    assert feats["width"] == 512.0
    assert feats["height"] == 512.0
    assert feats["aspect_ratio"] == 1.0


def test_rule_diagnostics():
    # Low resolution and dark features
    bad_features = {
        "width": 100.0,
        "height": 100.0,
        "aspect_ratio": 1.0,
        "resolution_mp": 0.01,
        "brightness_mean": 20.0,
        "brightness_std": 10.0,
        "contrast_rms": 10.0,
        "blur_score": 15.0,
        "edge_density": 0.01,
        "color_variance": 5.0,
        "subject_framing_score": 0.5,
    }
    diag = analyze_image_quality_rules(bad_features)
    assert not diag["is_acceptable"]
    assert len(diag["issues"]) > 0
    assert len(diag["tips"]) > 0


def test_predict_image_quality():
    artifact_path = os.path.join(PROJECT_ROOT, "ml", "artifacts", "image_quality_model.pkl")
    assert os.path.exists(artifact_path), "Artifact .pkl does not exist!"

    # Create dummy sharp image
    test_arr = (np.random.rand(600, 600, 3) * 255).astype(np.uint8)
    res = predict_image_quality(test_arr, artifact_path=artifact_path)

    assert "status" in res
    assert res["status"] in ["ready", "retake"]
    assert "confidence" in res
    assert 0.0 <= res["confidence"] <= 1.0
    assert "probabilities" in res
    assert "ready" in res["probabilities"]
    assert "retake" in res["probabilities"]
