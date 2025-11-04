from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import uuid
import os
import aiofiles
from ..core.database import get_db
from ..models import Character, CharacterFaceReference, CharacterOutfit
from ..schemas import character as schemas
from ..services import FaceEmbeddingService
from ..core.config import settings

router = APIRouter()
face_service = FaceEmbeddingService()


@router.post("/", response_model=schemas.Character)
async def create_character(
    character: schemas.CharacterCreate,
    db: Session = Depends(get_db)
):
    """Create a new character profile"""
    # Generate stable ID for cross-project reuse
    stable_id = f"char_{uuid.uuid4().hex[:12]}"

    db_character = Character(
        stable_id=stable_id,
        **character.model_dump()
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


@router.get("/", response_model=List[schemas.Character])
def get_characters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all characters"""
    characters = db.query(Character).offset(skip).limit(limit).all()
    return characters


@router.get("/{character_id}", response_model=schemas.Character)
def get_character(
    character_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.put("/{character_id}", response_model=schemas.Character)
def update_character(
    character_id: int,
    character_update: schemas.CharacterUpdate,
    db: Session = Depends(get_db)
):
    """Update a character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    update_data = character_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)

    db.commit()
    db.refresh(character)
    return character


@router.delete("/{character_id}")
def delete_character(
    character_id: int,
    db: Session = Depends(get_db)
):
    """Delete a character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    db.delete(character)
    db.commit()
    return {"message": "Character deleted successfully"}


@router.post("/{character_id}/face-references")
async def upload_face_reference(
    character_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a face reference image for a character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check number of existing references
    existing_refs = db.query(CharacterFaceReference).filter(
        CharacterFaceReference.character_id == character_id
    ).count()

    if existing_refs >= settings.MAX_FACE_EMBEDDINGS:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum of {settings.MAX_FACE_EMBEDDINGS} face references allowed"
        )

    # Save uploaded file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "face_references", str(character_id))
    os.makedirs(upload_dir, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(upload_dir, file_name)

    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    # Extract face embedding
    embedding_result = face_service.extract_embedding(file_path)

    if not embedding_result:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail="No face detected in the image"
        )

    # Create reference record
    face_ref = CharacterFaceReference(
        character_id=character_id,
        image_path=file_path,
        embedding=embedding_result["embedding"],
        quality_score=embedding_result["quality_score"]
    )
    db.add(face_ref)

    # Update character's averaged embedding
    all_refs = db.query(CharacterFaceReference).filter(
        CharacterFaceReference.character_id == character_id
    ).all()

    embeddings = [ref.embedding for ref in all_refs] + [embedding_result["embedding"]]
    averaged_embedding = face_service.average_embeddings(embeddings)

    character.face_embedding = averaged_embedding

    db.commit()
    db.refresh(face_ref)

    return {
        "message": "Face reference uploaded successfully",
        "reference_id": face_ref.id,
        "quality_score": face_ref.quality_score
    }


@router.post("/{character_id}/outfits", response_model=schemas.CharacterOutfit)
def create_outfit(
    character_id: int,
    outfit: schemas.CharacterOutfitCreate,
    db: Session = Depends(get_db)
):
    """Create an outfit for a character"""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    db_outfit = CharacterOutfit(
        character_id=character_id,
        **outfit.model_dump()
    )
    db.add(db_outfit)
    db.commit()
    db.refresh(db_outfit)
    return db_outfit


@router.get("/{character_id}/outfits", response_model=List[schemas.CharacterOutfit])
def get_character_outfits(
    character_id: int,
    db: Session = Depends(get_db)
):
    """Get all outfits for a character"""
    outfits = db.query(CharacterOutfit).filter(
        CharacterOutfit.character_id == character_id
    ).all()
    return outfits
