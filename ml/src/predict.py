"""
Inference and prediction module for the RetroMorph AI Image Readiness Classifier.
Can be used as a CLI tool or imported as a Python service.
"""

import os
import sys
import json
import joblib
import pandas as pd
from typing import Dict, Any, Union
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from features import extract_image_features, analyze_image_quality_rules, FEATURE_NAMES

_CACHED_ARTIFACT = None


def get_model(artifact_path: str = None):
    global _CACHED_ARTIFACT
    if _CACHED_ARTIFACT is not None:
        return _CACHED_ARTIFACT

    paths_to_check = [
        artifact_path,
        os.path.join(CURRENT_DIR, "..", "artifacts", "image_quality_model.pkl"),
        os.path.join(CURRENT_DIR, "..", "..", "backend", "models", "image_quality_model.pkl"),
        "ml/artifacts/image_quality_model.pkl",
        "backend/models/image_quality_model.pkl",
    ]

    for p in paths_to_check:
        if p and os.path.exists(p):
            _CACHED_ARTIFACT = joblib.load(p)
            return _CACHED_ARTIFACT

    raise FileNotFoundError(
        "Model artifact not found. Please run ml/src/train_model.py first."
    )


def predict_image_quality(
    image_input: Union[str, np.ndarray],
    artifact_path: str = None
) -> Dict[str, Any]:
    """
    Evaluates an uploaded image for 3D character generation readiness.

    Args:
        image_input: Filepath or numpy image array
        artifact_path: Optional custom path to model artifact

    Returns:
        Dict containing prediction ('ready' / 'retake'), confidence scores,
        extracted features, and human-friendly diagnostic advice.
    """
    features = extract_image_features(image_input)
    rule_analysis = analyze_image_quality_rules(features)

    artifact = get_model(artifact_path)
    pipeline = artifact["pipeline"]
    classes = list(pipeline.classes_)

    # Construct DataFrame with feature names
    X = pd.DataFrame([features])[FEATURE_NAMES]

    # Predict
    pred_label = pipeline.predict(X)[0]
    probabilities = pipeline.predict_proba(X)[0]
    prob_dict = {cls: round(float(prob), 4) for cls, prob in zip(classes, probabilities)}

    # Confidence in predicted label
    confidence = float(max(probabilities))

    # Formulate friendly recommendation
    is_ready = (pred_label == "ready")
    if is_ready:
        summary = "Image is suitable for PS1 character generation."
    else:
        summary = "Image has quality issues that will affect 3D generation. Consider retaking or replacing."

    return {
        "status": "ready" if is_ready else "retake",
        "is_ready": is_ready,
        "confidence": round(confidence, 4),
        "probabilities": prob_dict,
        "summary": summary,
        "features": features,
        "diagnostics": rule_analysis,
        "suggestions": rule_analysis["tips"] if not is_ready else ["Image clarity is good. Proceed with generation."],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_image>")
        sys.exit(1)

    target_image = sys.argv[1]
    result = predict_image_quality(target_image)
    print(json.dumps(result, indent=2))
