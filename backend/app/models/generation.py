from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base


class GenerationType(str, enum.Enum):
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_TO_VIDEO = "image_to_video"
    VIDEO_TO_VIDEO = "video_to_video"


class GenerationStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoQuality(str, enum.Enum):
    LOW = "low"      # Preview
    HIGH = "high"    # 4K final render


class VideoGeneration(Base):
    """Video generation job with Veo 3.1"""
    __tablename__ = "video_generations"

    id = Column(Integer, primary_key=True, index=True)

    # Generation type
    generation_type = Column(SQLEnum(GenerationType), nullable=False)
    quality = Column(SQLEnum(VideoQuality), default=VideoQuality.LOW)

    # Input
    prompt = Column(Text, nullable=False)
    aspect_ratio = Column(String(10), default="16:9")

    # Optional inputs
    input_image_path = Column(String(255), nullable=True)
    input_video_path = Column(String(255), nullable=True)

    # Character consistency
    character_id = Column(Integer, nullable=True)
    character_embedding = Column(JSON)  # Face embedding to maintain
    style_locks = Column(JSON)  # Locked style attributes

    # Status
    status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING)

    # Output
    output_video_path = Column(String(255), nullable=True)
    thumbnail_path = Column(String(255), nullable=True)

    # Veo response
    veo_job_id = Column(String(255), nullable=True)
    veo_response = Column(JSON)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    shot_versions = relationship("ShotVersion", back_populates="generation")
