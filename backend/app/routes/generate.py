"""
FastAPI route for submitting 3D character generation requests.
"""

import os
import shutil
import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException

from ..schemas.generator import (
    GenerationSettings,
    GenderPresentation,
    OutfitType,
    PolygonLevel,
    TextureSize,
    PoseType,
    JobResponse
)
from ..services.job_manager import (
    create_job,
    get_job,
    execute_generation_pipeline,
    UPLOADS_DIR
)

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate", response_model=JobResponse)
async def generate_character(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    gender: GenderPresentation = Form(GenderPresentation.MALE),
    outfit: OutfitType = Form(OutfitType.CASUAL),
    custom_outfit: Optional[str] = Form(None),
    polygon_level: PolygonLevel = Form(PolygonLevel.MEDIUM),
    texture_size: TextureSize = Form(TextureSize.SIZE_128),
    pose: PoseType = Form(PoseType.STANDING),
    enable_affine_jitter: bool = Form(False),
    enable_retro_dither: bool = Form(True)
):
    """
    Submits a photo and generation parameters to the RetroMorph pipeline.
    Runs asynchronously and returns a job object to track progress.
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    file_ext = os.path.splitext(image.filename)[1] or ".jpg"
    saved_filename = f"upload_{uuid.uuid4().hex[:12]}{file_ext}"
    saved_path = os.path.join(UPLOADS_DIR, saved_filename)

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    settings = GenerationSettings(
        gender=gender,
        outfit=outfit,
        custom_outfit=custom_outfit,
        polygon_level=polygon_level,
        texture_size=texture_size,
        pose=pose,
        enable_affine_jitter=enable_affine_jitter,
        enable_retro_dither=enable_retro_dither
    )

    job_id = create_job(settings)

    # Launch background async task
    background_tasks.add_task(
        execute_generation_pipeline,
        job_id=job_id,
        input_image_path=saved_path,
        settings=settings
    )

    job_data = get_job(job_id)
    return JobResponse(
        job_id=job_id,
        status=job_data["status"],
        progress=job_data["progress"],
        current_stage=job_data["current_stage"],
        created_at=job_data["created_at"],
        updated_at=job_data["updated_at"],
        preview_url=f"/api/jobs/{job_id}/preview",
        model_url=f"/api/jobs/{job_id}/model",
        metadata=job_data.get("quality_report")
    )
