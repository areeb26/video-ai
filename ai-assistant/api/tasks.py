"""
Task API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..services.task_manager import TaskManager

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task"""
    manager = TaskManager(db)
    return manager.create_task(task)


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(None, regex="^(pending|in_progress|completed|cancelled)$"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high|urgent)$"),
    category: Optional[str] = None,
    language: Optional[str] = Query(None, regex="^(en|ur)$"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all tasks with optional filtering"""
    manager = TaskManager(db)
    return manager.get_all_tasks(status, priority, category, language, skip, limit)


@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """Get tasks summary"""
    manager = TaskManager(db)
    return manager.get_tasks_summary()


@router.get("/overdue", response_model=List[TaskResponse])
async def get_overdue_tasks(db: Session = Depends(get_db)):
    """Get overdue tasks"""
    manager = TaskManager(db)
    return manager.get_overdue_tasks()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task"""
    manager = TaskManager(db)
    task = manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    """Update a task"""
    manager = TaskManager(db)
    task = manager.update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task"""
    manager = TaskManager(db)
    success = manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Mark a task as completed"""
    manager = TaskManager(db)
    task = manager.complete_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
