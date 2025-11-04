from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class BeatType(str, enum.Enum):
    HOOK = "hook"
    CONFLICT = "conflict"
    RESOLUTION = "resolution"
    CUSTOM = "custom"


class ShotType(str, enum.Enum):
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE = "close"
    EXTREME_CLOSE = "extreme_close"


class CameraPath(str, enum.Enum):
    DOLLY = "dolly"
    PAN = "pan"
    ORBIT = "orbit"
    STATIC = "static"
    TILT = "tilt"
    ZOOM = "zoom"


class Project(Base):
    """Story project with timeline"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    beats = relationship("Beat", back_populates="project", cascade="all, delete-orphan", order_by="Beat.order")


class Beat(Base):
    """Beat in the timeline: hook, conflict, resolution"""
    __tablename__ = "beats"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))

    beat_type = Column(SQLEnum(BeatType), nullable=False)
    order = Column(Integer, nullable=False)  # Sequence in timeline

    title = Column(String(200))
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    project = relationship("Project", back_populates="beats")
    shots = relationship("Shot", back_populates="beat", cascade="all, delete-orphan", order_by="Shot.order")


class Shot(Base):
    """Individual shot in a beat"""
    __tablename__ = "shots"

    id = Column(Integer, primary_key=True, index=True)
    beat_id = Column(Integer, ForeignKey("beats.id", ondelete="CASCADE"))
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="SET NULL"), nullable=True)

    order = Column(Integer, nullable=False)
    shot_type = Column(SQLEnum(ShotType), nullable=False)
    camera_path = Column(SQLEnum(CameraPath), nullable=False)

    # Per-shot prompt fields
    character_prompt = Column(Text)  # Character description
    setting_prompt = Column(Text)    # Setting/location
    action_prompt = Column(Text)     # What's happening
    mood_prompt = Column(Text)       # Mood/atmosphere
    camera_prompt = Column(Text)     # Camera movement details

    # Combined full prompt
    full_prompt = Column(Text)

    # Aspect ratio
    aspect_ratio = Column(String(10), default="16:9")  # 9:16, 1:1, 16:9, 4:5

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    beat = relationship("Beat", back_populates="shots")
    character = relationship("Character", back_populates="shots")
    versions = relationship("ShotVersion", back_populates="shot", cascade="all, delete-orphan", order_by="ShotVersion.version_number")


class ShotVersion(Base):
    """Versioning for each shot"""
    __tablename__ = "shot_versions"

    id = Column(Integer, primary_key=True, index=True)
    shot_id = Column(Integer, ForeignKey("shots.id", ondelete="CASCADE"))

    version_number = Column(Integer, nullable=False)

    # Generation details
    generation_id = Column(Integer, ForeignKey("video_generations.id", ondelete="SET NULL"), nullable=True)

    # Continuity score
    continuity_score = Column(JSON)  # {"face_similarity": 0.95, "style_match": 0.92}
    drift_flags = Column(JSON)  # ["hair_color_drift", "outfit_mismatch"]

    notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shot = relationship("Shot", back_populates="versions")
    generation = relationship("VideoGeneration", back_populates="shot_versions")
