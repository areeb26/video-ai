from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..models import Project, Beat, Shot, ShotVersion
from ..schemas import project as schemas

router = APIRouter()


@router.post("/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new project"""
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/", response_model=List[schemas.Project])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all projects"""
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=schemas.Project)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific project with all beats and shots"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db)
):
    """Update a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


# Beat endpoints
@router.post("/{project_id}/beats", response_model=schemas.Beat)
def create_beat(
    project_id: int,
    beat: schemas.BeatCreate,
    db: Session = Depends(get_db)
):
    """Create a new beat in the project timeline"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_beat = Beat(project_id=project_id, **beat.model_dump())
    db.add(db_beat)
    db.commit()
    db.refresh(db_beat)
    return db_beat


@router.get("/{project_id}/beats", response_model=List[schemas.Beat])
def get_project_beats(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get all beats for a project"""
    beats = db.query(Beat).filter(Beat.project_id == project_id).order_by(Beat.order).all()
    return beats


@router.put("/beats/{beat_id}", response_model=schemas.Beat)
def update_beat(
    beat_id: int,
    beat_update: schemas.BeatUpdate,
    db: Session = Depends(get_db)
):
    """Update a beat"""
    beat = db.query(Beat).filter(Beat.id == beat_id).first()
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")

    update_data = beat_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(beat, field, value)

    db.commit()
    db.refresh(beat)
    return beat


# Shot endpoints
@router.post("/beats/{beat_id}/shots", response_model=schemas.Shot)
def create_shot(
    beat_id: int,
    shot: schemas.ShotCreate,
    db: Session = Depends(get_db)
):
    """Create a new shot in a beat"""
    beat = db.query(Beat).filter(Beat.id == beat_id).first()
    if not beat:
        raise HTTPException(status_code=404, detail="Beat not found")

    # Build full prompt from components
    prompt_parts = []
    if shot.character_prompt:
        prompt_parts.append(f"Character: {shot.character_prompt}")
    if shot.setting_prompt:
        prompt_parts.append(f"Setting: {shot.setting_prompt}")
    if shot.action_prompt:
        prompt_parts.append(f"Action: {shot.action_prompt}")
    if shot.mood_prompt:
        prompt_parts.append(f"Mood: {shot.mood_prompt}")
    if shot.camera_prompt:
        prompt_parts.append(f"Camera: {shot.camera_prompt}")

    full_prompt = ". ".join(prompt_parts)

    db_shot = Shot(
        beat_id=beat_id,
        full_prompt=full_prompt,
        **shot.model_dump()
    )
    db.add(db_shot)
    db.commit()
    db.refresh(db_shot)
    return db_shot


@router.get("/beats/{beat_id}/shots", response_model=List[schemas.Shot])
def get_beat_shots(
    beat_id: int,
    db: Session = Depends(get_db)
):
    """Get all shots for a beat"""
    shots = db.query(Shot).filter(Shot.beat_id == beat_id).order_by(Shot.order).all()
    return shots


@router.put("/shots/{shot_id}", response_model=schemas.Shot)
def update_shot(
    shot_id: int,
    shot_update: schemas.ShotUpdate,
    db: Session = Depends(get_db)
):
    """Update a shot"""
    shot = db.query(Shot).filter(Shot.id == shot_id).first()
    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")

    update_data = shot_update.model_dump(exclude_unset=True)

    # Rebuild full prompt if prompt components changed
    if any(field in update_data for field in ['character_prompt', 'setting_prompt', 'action_prompt', 'mood_prompt', 'camera_prompt']):
        prompt_parts = []
        char_prompt = update_data.get('character_prompt', shot.character_prompt)
        setting_prompt = update_data.get('setting_prompt', shot.setting_prompt)
        action_prompt = update_data.get('action_prompt', shot.action_prompt)
        mood_prompt = update_data.get('mood_prompt', shot.mood_prompt)
        camera_prompt = update_data.get('camera_prompt', shot.camera_prompt)

        if char_prompt:
            prompt_parts.append(f"Character: {char_prompt}")
        if setting_prompt:
            prompt_parts.append(f"Setting: {setting_prompt}")
        if action_prompt:
            prompt_parts.append(f"Action: {action_prompt}")
        if mood_prompt:
            prompt_parts.append(f"Mood: {mood_prompt}")
        if camera_prompt:
            prompt_parts.append(f"Camera: {camera_prompt}")

        update_data['full_prompt'] = ". ".join(prompt_parts)

    for field, value in update_data.items():
        setattr(shot, field, value)

    db.commit()
    db.refresh(shot)
    return shot
