from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.generation import GenerationType, GenerationStatus, VideoQuality


class VideoGenerationCreate(BaseModel):
    generation_type: GenerationType
    prompt: str = Field(..., min_length=1)
    aspect_ratio: str = "16:9"
    quality: VideoQuality = VideoQuality.LOW

    # Optional inputs
    character_id: Optional[int] = None
    input_image_path: Optional[str] = None
    input_video_path: Optional[str] = None
    style_locks: Optional[dict] = None


class VideoGeneration(BaseModel):
    id: int
    generation_type: GenerationType
    quality: VideoQuality
    prompt: str
    aspect_ratio: str
    input_image_path: Optional[str] = None
    input_video_path: Optional[str] = None
    character_id: Optional[int] = None
    character_embedding: Optional[List[float]] = None
    style_locks: Optional[dict] = None
    status: GenerationStatus
    output_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    veo_job_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
