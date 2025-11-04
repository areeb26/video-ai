from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ..models.project import BeatType, ShotType, CameraPath


class ShotVersionBase(BaseModel):
    version_number: int
    notes: Optional[str] = None


class ShotVersion(ShotVersionBase):
    id: int
    shot_id: int
    generation_id: Optional[int] = None
    continuity_score: Optional[dict] = None
    drift_flags: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ShotBase(BaseModel):
    shot_type: ShotType
    camera_path: CameraPath
    character_prompt: Optional[str] = None
    setting_prompt: Optional[str] = None
    action_prompt: Optional[str] = None
    mood_prompt: Optional[str] = None
    camera_prompt: Optional[str] = None
    aspect_ratio: str = "16:9"


class ShotCreate(ShotBase):
    character_id: Optional[int] = None
    order: int


class ShotUpdate(BaseModel):
    shot_type: Optional[ShotType] = None
    camera_path: Optional[CameraPath] = None
    character_id: Optional[int] = None
    character_prompt: Optional[str] = None
    setting_prompt: Optional[str] = None
    action_prompt: Optional[str] = None
    mood_prompt: Optional[str] = None
    camera_prompt: Optional[str] = None
    aspect_ratio: Optional[str] = None
    full_prompt: Optional[str] = None


class Shot(ShotBase):
    id: int
    beat_id: int
    character_id: Optional[int] = None
    order: int
    full_prompt: Optional[str] = None
    created_at: datetime
    versions: List[ShotVersion] = []

    class Config:
        from_attributes = True


class BeatBase(BaseModel):
    beat_type: BeatType
    title: Optional[str] = None
    description: Optional[str] = None


class BeatCreate(BeatBase):
    order: int


class BeatUpdate(BaseModel):
    beat_type: Optional[BeatType] = None
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None


class Beat(BeatBase):
    id: int
    project_id: int
    order: int
    created_at: datetime
    shots: List[Shot] = []

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    beats: List[Beat] = []

    class Config:
        from_attributes = True
