"""
Quality Service for FastAPI backend.
Integrates the trained scikit-learn Image Readiness Model to validate user uploads.
"""

import os
import sys
from typing import Dict, Any, Union
from PIL import Image

# Import from ml/src
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ML_SRC = os.path.join(PROJECT_ROOT, "ml", "src")
if ML_SRC not in sys.path:
    sys.path.append(ML_SRC)

from predict import predict_image_quality


def check_image_readiness(image_path: str) -> Dict[str, Any]:
    """
    Evaluates an uploaded user photo using the trained .pkl model.
    """
    artifact_path = os.path.join(
        PROJECT_ROOT, "backend", "models", "image_quality_model.pkl"
    )
    if not os.path.exists(artifact_path):
        artifact_path = os.path.join(
            PROJECT_ROOT, "ml", "artifacts", "image_quality_model.pkl"
        )

    return predict_image_quality(image_path, artifact_path=artifact_path)
