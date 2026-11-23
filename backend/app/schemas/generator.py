"""
Pydantic schemas and models for the RetroMorph AI character generator.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class GenderPresentation(str, Enum):
    MALE = "male"
    FEMALE = "female"
    CUSTOM = "custom"


class OutfitType(str, Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    POLICE = "police"
    HORROR = "horror"
    TRADITIONAL = "traditional"
    CUSTOM = "custom"


class PolygonLevel(str, Enum):
    LOW = "low"         # ~1000 - 1500 triangles
    MEDIUM = "medium"   # ~2500 triangles
    HIGH = "high"       # ~5000 triangles


class TextureSize(int, Enum):
    SIZE_64 = 64
    SIZE_128 = 128
    SIZE_256 = 256


class PoseType(str, Enum):
    T_POSE = "t_pose"
    STANDING = "standing"


class GenerationSettings(BaseModel):
    gender: GenderPresentation = GenderPresentation.MALE
    outfit: OutfitType = OutfitType.CASUAL
    custom_outfit: Optional[str] = None
    polygon_level: PolygonLevel = PolygonLevel.MEDIUM
    texture_size: TextureSize = TextureSize.SIZE_128
    pose: PoseType = PoseType.STANDING
    enable_affine_jitter: bool = False
    enable_retro_dither: bool = True


class QualityDiagnostics(BaseModel):
    is_acceptable: bool
    issues: List[str]
    tips: List[str]


class QualityCheckResponse(BaseModel):
    status: str
    is_ready: bool
    confidence: float
    probabilities: Dict[str, float]
    summary: str
    features: Dict[str, float]
    diagnostics: QualityDiagnostics
    suggestions: List[str]


class JobStatus(str, Enum):
    QUEUED = "queued"
    CHECKING_QUALITY = "checking_quality"
    GENERATING_CONCEPT = "generating_concept"
    GENERATING_3D = "generating_3d"
    OPTIMIZING_MESH = "optimizing_mesh"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    current_stage: str
    error: Optional[str] = None
    created_at: str
    updated_at: str
    preview_url: Optional[str] = None
    model_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
