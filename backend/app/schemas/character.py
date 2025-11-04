from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CharacterOutfitBase(BaseModel):
    slot_name: str = Field(..., description="Outfit slot: casual, formal, hero, winter")
    description: Optional[str] = None
    top: Optional[str] = None
    bottom: Optional[str] = None
    shoes: Optional[str] = None
    accessories: Optional[List[str]] = None
    colors: Optional[List[str]] = None


class CharacterOutfitCreate(CharacterOutfitBase):
    pass


class CharacterOutfit(CharacterOutfitBase):
    id: int
    character_id: int
    reference_image_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CharacterFaceReferenceBase(BaseModel):
    image_path: str


class CharacterFaceReference(CharacterFaceReferenceBase):
    id: int
    character_id: int
    quality_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    body_shape: Optional[str] = None
    hair_color: Optional[str] = None
    hair_style: Optional[str] = None
    skin_tone: Optional[str] = None
    eye_color: Optional[str] = None
    height: Optional[str] = None
    color_palette: Optional[List[str]] = None
    accessories: Optional[List[str]] = None
    negative_traits: Optional[List[str]] = None


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    body_shape: Optional[str] = None
    hair_color: Optional[str] = None
    hair_style: Optional[str] = None
    skin_tone: Optional[str] = None
    eye_color: Optional[str] = None
    height: Optional[str] = None
    color_palette: Optional[List[str]] = None
    accessories: Optional[List[str]] = None
    negative_traits: Optional[List[str]] = None


class Character(CharacterBase):
    id: int
    stable_id: str
    face_embedding: Optional[List[float]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    face_references: List[CharacterFaceReference] = []
    outfits: List[CharacterOutfit] = []

    class Config:
        from_attributes = True
