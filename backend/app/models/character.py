from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Character(Base):
    """Character profile with locked traits for consistency"""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    stable_id = Column(String(50), unique=True, index=True)  # Reusable across projects
    name = Column(String(100), nullable=False)
    age = Column(Integer)

    # Physical traits (locked)
    body_shape = Column(String(50))  # slim, athletic, stocky, etc.
    hair_color = Column(String(50))
    hair_style = Column(String(100))
    skin_tone = Column(String(50))
    eye_color = Column(String(50))
    height = Column(String(50))  # tall, average, short

    # Style locks
    color_palette = Column(JSON)  # ["#FF5733", "#33FF57", ...]
    accessories = Column(JSON)  # ["glasses", "watch", "necklace"]

    # Negative traits to avoid drift
    negative_traits = Column(JSON)  # ["different hair", "wrong eye color", ...]

    # Face embedding (averaged from references)
    face_embedding = Column(JSON)  # Stored as array

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    face_references = relationship("CharacterFaceReference", back_populates="character", cascade="all, delete-orphan")
    outfits = relationship("CharacterOutfit", back_populates="character", cascade="all, delete-orphan")
    shots = relationship("Shot", back_populates="character")


class CharacterFaceReference(Base):
    """Reference images for face embeddings (3-10 images)"""
    __tablename__ = "character_face_references"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"))

    image_path = Column(String(255), nullable=False)
    embedding = Column(JSON)  # Face embedding from this image
    quality_score = Column(Float)  # How good this reference is

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    character = relationship("Character", back_populates="face_references")


class CharacterOutfit(Base):
    """Outfit slots: casual, formal, hero, winter, etc."""
    __tablename__ = "character_outfits"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"))

    slot_name = Column(String(50), nullable=False)  # casual, formal, hero, winter
    description = Column(Text)  # Detailed description of the outfit
    reference_image_path = Column(String(255))

    # Outfit details
    top = Column(String(200))
    bottom = Column(String(200))
    shoes = Column(String(200))
    accessories = Column(JSON)
    colors = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    character = relationship("Character", back_populates="outfits")
