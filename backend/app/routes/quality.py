"""
FastAPI route for instant ML image quality readiness assessment.
"""

import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..schemas.generator import QualityCheckResponse
from ..services.quality_service import check_image_readiness

router = APIRouter(prefix="/api", tags=["quality"])


@router.post("/check-quality", response_model=QualityCheckResponse)
async def check_quality_endpoint(image: UploadFile = File(...)):
    """
    Evaluates an uploaded image using the trained scikit-learn Image Readiness Classifier (.pkl).
    Returns ready/retake status, class probabilities, and diagnostic tips.
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image.")

    # Save to temp file for analysis
    suffix = os.path.splitext(image.filename)[1] or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(image.file, tmp)
        tmp_path = tmp.name

    try:
        result = check_image_readiness(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
