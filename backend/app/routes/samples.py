"""
Pre-packaged sample images route for immediate testing.
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/samples", tags=["samples"])

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SAMPLES_DIR = os.path.join(PROJECT_ROOT, "ml", "data", "samples")


@router.get("")
async def list_sample_images():
    """
    Returns a list of sample images for 1-click testing in the UI.
    """
    if not os.path.exists(SAMPLES_DIR):
        return {"samples": []}

    files = [f for f in os.listdir(SAMPLES_DIR) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
    samples = []
    for f in sorted(files)[:12]:
        is_ready = "ready" in f.lower()
        samples.append({
            "filename": f,
            "title": f.replace("sample_", "").replace(".jpg", "").replace("_", " ").title(),
            "expected_label": "ready" if is_ready else "retake",
            "url": f"/api/samples/{f}"
        })
    return {"samples": samples}


@router.get("/{filename}")
async def get_sample_file(filename: str):
    """
    Retrieves a sample photo file.
    """
    file_path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample not found.")
    return FileResponse(file_path, media_type="image/jpeg")
