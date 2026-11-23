"""
Asynchronous Job Manager for RetroMorph AI Character Generator.
Orchestrates pipeline execution, tracks progress, and manages artifacts.
"""

import os
import uuid
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from ..schemas.generator import JobStatus, GenerationSettings
from .quality_service import check_image_readiness
from .ps1_concept_service import generate_ps1_concept_art
from .mesh_generator_service import (
    generate_retro_texture_atlas,
    build_ps1_humanoid_mesh,
    export_character_glb
)
from .blender_service import run_blender_optimization

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
GENERATED_DIR = os.path.join(PROJECT_ROOT, "backend", "generated")
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "backend", "uploads")

# In-memory job cache
_JOBS: Dict[str, Dict[str, Any]] = {}


def create_job(settings: GenerationSettings) -> str:
    """Creates a new queued generation job."""
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(GENERATED_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    job_data = {
        "job_id": job_id,
        "status": JobStatus.QUEUED.value,
        "progress": 0,
        "current_stage": "Job queued for processing",
        "error": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "settings": settings.model_dump(),
        "files": {
            "source_image": None,
            "preview_image": None,
            "texture_map": None,
            "model_glb": None,
        },
        "quality_report": None,
    }

    _JOBS[job_id] = job_data
    save_job_metadata(job_id)
    return job_id


def save_job_metadata(job_id: str):
    """Saves job state to disk for persistence."""
    if job_id not in _JOBS:
        return
    job_dir = os.path.join(GENERATED_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    meta_path = os.path.join(job_dir, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(_JOBS[job_id], f, indent=2)


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves job state from memory or disk."""
    if job_id in _JOBS:
        return _JOBS[job_id]

    meta_path = os.path.join(GENERATED_DIR, job_id, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            data = json.load(f)
            _JOBS[job_id] = data
            return data
    return None


def update_job_stage(job_id: str, status: JobStatus, progress: int, stage_desc: str, error: str = None):
    """Updates job status and timestamp."""
    if job_id not in _JOBS:
        return
    _JOBS[job_id]["status"] = status.value
    _JOBS[job_id]["progress"] = progress
    _JOBS[job_id]["current_stage"] = stage_desc
    _JOBS[job_id]["updated_at"] = datetime.now().isoformat()
    if error:
        _JOBS[job_id]["error"] = error
    save_job_metadata(job_id)


async def execute_generation_pipeline(job_id: str, input_image_path: str, settings: GenerationSettings):
    """
    Executes the multi-stage RetroMorph AI character generation pipeline.
    """
    job_dir = os.path.join(GENERATED_DIR, job_id)
    _JOBS[job_id]["files"]["source_image"] = input_image_path

    try:
        # -------------------------------------------------------------
        # Stage 1: Quality Check (ML Model Assessment)
        # -------------------------------------------------------------
        update_job_stage(
            job_id,
            JobStatus.CHECKING_QUALITY,
            15,
            "Assessing image quality with ML Readiness Classifier..."
        )
        await asyncio.sleep(0.3)  # Gentle async yield
        
        quality_res = check_image_readiness(input_image_path)
        _JOBS[job_id]["quality_report"] = quality_res

        # Even if quality is marginal, we proceed with warnings recorded in metadata
        
        # -------------------------------------------------------------
        # Stage 2: 2D PS1 Concept Art Generation
        # -------------------------------------------------------------
        update_job_stage(
            job_id,
            JobStatus.GENERATING_CONCEPT,
            40,
            f"Generating 2D PS1 retro concept ({settings.gender.value}, {settings.outfit.value})..."
        )
        await asyncio.sleep(0.3)

        preview_path = os.path.join(job_dir, "concept_preview.png")
        generate_ps1_concept_art(
            image_path=input_image_path,
            output_path=preview_path,
            gender=settings.gender.value,
            outfit=settings.outfit.value,
            custom_outfit=settings.custom_outfit
        )
        _JOBS[job_id]["files"]["preview_image"] = preview_path

        # -------------------------------------------------------------
        # Stage 3: Low-Poly 3D Mesh Generation & Retro Texture Baking
        # -------------------------------------------------------------
        update_job_stage(
            job_id,
            JobStatus.GENERATING_3D,
            65,
            f"Synthesizing low-poly 3D geometry and {settings.texture_size.value}x{settings.texture_size.value} texture atlas..."
        )
        await asyncio.sleep(0.3)

        texture_path = os.path.join(job_dir, f"texture_{settings.texture_size.value}.png")
        generate_retro_texture_atlas(
            source_img_path=input_image_path,
            output_texture_path=texture_path,
            texture_size=settings.texture_size.value,
            outfit=settings.outfit.value,
            gender=settings.gender.value
        )
        _JOBS[job_id]["files"]["texture_map"] = texture_path

        # Build humanoid 3D geometry
        mesh = build_ps1_humanoid_mesh(
            gender=settings.gender.value,
            outfit=settings.outfit.value,
            pose=settings.pose.value,
            texture_path=texture_path
        )

        intermediate_obj = os.path.join(job_dir, "raw_mesh.obj")
        mesh.export(intermediate_obj)

        final_glb = os.path.join(job_dir, "character_model.glb")

        # -------------------------------------------------------------
        # Stage 4: Blender Optimization / Final Export
        # -------------------------------------------------------------
        update_job_stage(
            job_id,
            JobStatus.OPTIMIZING_MESH,
            85,
            f"Applying retro decimation ({settings.polygon_level.value}) and GLB compilation..."
        )
        await asyncio.sleep(0.3)

        # Attempt Blender headless optimization
        blender_success = run_blender_optimization(
            input_model_path=intermediate_obj,
            output_glb_path=final_glb,
            polygon_level=settings.polygon_level.value,
            texture_path=texture_path,
            texture_size=settings.texture_size.value,
            enable_affine_jitter=settings.enable_affine_jitter
        )

        # Fallback to direct trimesh export if Blender is not run or encountered issue
        if not blender_success or not os.path.exists(final_glb):
            export_character_glb(mesh, final_glb, texture_path=texture_path)

        _JOBS[job_id]["files"]["model_glb"] = final_glb

        # -------------------------------------------------------------
        # Completion
        # -------------------------------------------------------------
        update_job_stage(
            job_id,
            JobStatus.COMPLETED,
            100,
            "Character generation complete! 3D GLB asset ready for download and preview."
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        update_job_stage(
            job_id,
            JobStatus.FAILED,
            _JOBS[job_id].get("progress", 0),
            "Generation encountered an error.",
            error=str(e)
        )
