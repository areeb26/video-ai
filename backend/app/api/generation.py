from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models import VideoGeneration, Character, Shot, ShotVersion
from ..models.generation import GenerationStatus, GenerationType
from ..schemas import generation as schemas
from ..services import VeoService, ContinuityValidator
from ..core.config import settings
import asyncio

router = APIRouter()
veo_service = VeoService()
continuity_validator = ContinuityValidator()


@router.post("/", response_model=schemas.VideoGeneration)
async def create_generation(
    generation: schemas.VideoGenerationCreate,
    db: Session = Depends(get_db)
):
    """Create a new video generation job"""

    # Get character embedding if character_id provided
    character_embedding = None
    style_locks = generation.style_locks or {}

    if generation.character_id:
        character = db.query(Character).filter(
            Character.id == generation.character_id
        ).first()

        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        character_embedding = character.face_embedding

        # Add character traits to style locks
        if character.hair_color:
            style_locks["hair_color"] = character.hair_color
        if character.skin_tone:
            style_locks["skin_tone"] = character.skin_tone
        if character.eye_color:
            style_locks["eye_color"] = character.eye_color
        if character.color_palette:
            style_locks["color_palette"] = character.color_palette
        if character.negative_traits:
            style_locks["negative_traits"] = character.negative_traits

    # Create generation record
    db_generation = VideoGeneration(
        generation_type=generation.generation_type,
        quality=generation.quality,
        prompt=generation.prompt,
        aspect_ratio=generation.aspect_ratio,
        input_image_path=generation.input_image_path,
        input_video_path=generation.input_video_path,
        character_id=generation.character_id,
        character_embedding=character_embedding,
        style_locks=style_locks,
        status=GenerationStatus.PENDING
    )

    db.add(db_generation)
    db.commit()
    db.refresh(db_generation)

    # Start generation asynchronously
    # Note: In production, you'd use a task queue like Celery
    asyncio.create_task(process_generation(db_generation.id))

    return db_generation


async def process_generation(generation_id: int):
    """Process video generation in background"""
    from ..core.database import SessionLocal

    db = SessionLocal()
    try:
        generation = db.query(VideoGeneration).filter(
            VideoGeneration.id == generation_id
        ).first()

        if not generation:
            return

        # Update status to processing
        generation.status = GenerationStatus.PROCESSING
        db.commit()

        # Call Veo service
        result = await veo_service.generate_video(
            prompt=generation.prompt,
            aspect_ratio=generation.aspect_ratio,
            quality=generation.quality.value,
            input_image=generation.input_image_path,
            input_video=generation.input_video_path,
            character_embedding=generation.character_embedding,
            style_locks=generation.style_locks
        )

        if result["success"]:
            generation.status = GenerationStatus.COMPLETED
            generation.veo_job_id = result.get("job_id")
            generation.output_video_path = result.get("video_url")
            generation.veo_response = result.get("response")
        else:
            generation.status = GenerationStatus.FAILED
            generation.error_message = result.get("error")

        db.commit()

    except Exception as e:
        generation.status = GenerationStatus.FAILED
        generation.error_message = str(e)
        db.commit()

    finally:
        db.close()


@router.get("/", response_model=List[schemas.VideoGeneration])
def get_generations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[GenerationStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all video generations"""
    query = db.query(VideoGeneration)

    if status:
        query = query.filter(VideoGeneration.status == status)

    generations = query.offset(skip).limit(limit).all()
    return generations


@router.get("/{generation_id}", response_model=schemas.VideoGeneration)
def get_generation(
    generation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific generation"""
    generation = db.query(VideoGeneration).filter(
        VideoGeneration.id == generation_id
    ).first()

    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")

    return generation


@router.post("/{generation_id}/validate-continuity")
async def validate_generation_continuity(
    generation_id: int,
    db: Session = Depends(get_db)
):
    """Validate continuity for a generated video"""
    generation = db.query(VideoGeneration).filter(
        VideoGeneration.id == generation_id
    ).first()

    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")

    if not generation.output_video_path:
        raise HTTPException(
            status_code=400,
            detail="No output video available for validation"
        )

    if not generation.character_embedding:
        raise HTTPException(
            status_code=400,
            detail="No character reference available for validation"
        )

    # Validate continuity
    result = continuity_validator.validate_shot_continuity(
        reference_embedding=generation.character_embedding,
        shot_video_path=generation.output_video_path,
        style_locks=generation.style_locks
    )

    return result


@router.post("/shots/{shot_id}/generate", response_model=schemas.VideoGeneration)
async def generate_for_shot(
    shot_id: int,
    quality: str = "low",
    db: Session = Depends(get_db)
):
    """Generate video for a specific shot"""
    shot = db.query(Shot).filter(Shot.id == shot_id).first()

    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")

    # Create generation request
    generation_data = schemas.VideoGenerationCreate(
        generation_type=GenerationType.TEXT_TO_VIDEO,
        prompt=shot.full_prompt or "",
        aspect_ratio=shot.aspect_ratio,
        quality=quality,
        character_id=shot.character_id
    )

    # Create generation
    generation = await create_generation(generation_data, db)

    # Create shot version
    version_number = db.query(ShotVersion).filter(
        ShotVersion.shot_id == shot_id
    ).count() + 1

    shot_version = ShotVersion(
        shot_id=shot_id,
        version_number=version_number,
        generation_id=generation.id
    )
    db.add(shot_version)
    db.commit()

    return generation
