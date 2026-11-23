"""
Health check route for RetroMorph AI API.
"""

import os
from fastapi import APIRouter
from ..services.blender_service import find_blender_binary

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """
    Checks backend health, model artifact availability, and Blender status.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    model_path = os.path.join(project_root, "backend", "models", "image_quality_model.pkl")
    blender_path = find_blender_binary()

    return {
        "status": "online",
        "service": "RetroMorph AI - PS1 Character Generator Backend",
        "ml_model_loaded": os.path.exists(model_path),
        "blender_available": blender_path is not None,
        "blender_path": blender_path,
        "version": "1.0.0"
    }
