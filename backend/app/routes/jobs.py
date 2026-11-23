"""
FastAPI route for tracking job status and downloading generated assets.
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from ..schemas.generator import JobResponse
from ..services.job_manager import get_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """
    Checks status and progress of a character generation job.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    return JobResponse(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        current_stage=job["current_stage"],
        error=job.get("error"),
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        preview_url=f"/api/jobs/{job_id}/preview" if job["files"].get("preview_image") else None,
        model_url=f"/api/jobs/{job_id}/model" if job["files"].get("model_glb") else None,
        metadata={
            "settings": job.get("settings"),
            "quality": job.get("quality_report"),
        }
    )


@router.get("/{job_id}/preview")
async def get_job_preview(job_id: str):
    """
    Retrieves the 2D PS1 concept art preview image.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    preview_path = job["files"].get("preview_image")
    if not preview_path or not os.path.exists(preview_path):
        raise HTTPException(status_code=404, detail="Preview not ready yet.")

    return FileResponse(
        preview_path,
        media_type="image/png",
        filename=f"ps1_concept_{job_id[:8]}.png"
    )


@router.get("/{job_id}/model")
async def get_job_model(job_id: str):
    """
    Downloads the generated 3D low-poly character GLB.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    model_path = job["files"].get("model_glb")
    if not model_path or not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="3D Model not ready yet.")

    return FileResponse(
        model_path,
        media_type="model/gltf-binary",
        filename=f"ps1_character_{job_id[:8]}.glb"
    )


@router.get("/{job_id}/texture")
async def get_job_texture(job_id: str):
    """
    Downloads the baked retro UV texture map.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    texture_path = job["files"].get("texture_map")
    if not texture_path or not os.path.exists(texture_path):
        raise HTTPException(status_code=404, detail="Texture not found.")

    return FileResponse(
        texture_path,
        media_type="image/png",
        filename=f"retro_texture_{job_id[:8]}.png"
    )


@router.get("/{job_id}/report")
async def get_job_report(job_id: str):
    """
    Retrieves the detailed quality report and job metadata.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    return JSONResponse(content=job)
