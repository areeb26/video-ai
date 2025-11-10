"""
Task Management Service
Handles CRUD operations for tasks
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate


class TaskManager:
    """Service for managing tasks"""

    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task"""
        task = Task(**task_data.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_all_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        language: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get all tasks with optional filtering"""
        query = self.db.query(Task)

        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if category:
            query = query.filter(Task.category == category)
        if language:
            query = query.filter(Task.language == language)

        return query.offset(skip).limit(limit).all()

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Update an existing task"""
        task = self.get_task(task_id)
        if not task:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        task = self.get_task(task_id)
        if not task:
            return False

        self.db.delete(task)
        self.db.commit()
        return True

    def complete_task(self, task_id: int) -> Optional[Task]:
        """Mark a task as completed"""
        task = self.get_task(task_id)
        if not task:
            return None

        task.status = "completed"
        task.completed_at = datetime.now()
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_pending_reminders(self) -> List[Task]:
        """Get tasks with pending reminders"""
        now = datetime.now()
        return self.db.query(Task).filter(
            Task.reminder_enabled == True,
            Task.reminder_sent == False,
            Task.reminder_time <= now,
            Task.status != "completed"
        ).all()

    def mark_reminder_sent(self, task_id: int) -> bool:
        """Mark reminder as sent for a task"""
        task = self.get_task(task_id)
        if not task:
            return False

        task.reminder_sent = True
        self.db.commit()
        return True

    def get_tasks_by_tag(self, tag: str) -> List[Task]:
        """Get tasks by tag"""
        return self.db.query(Task).filter(Task.tags.like(f"%{tag}%")).all()

    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        now = datetime.now()
        return self.db.query(Task).filter(
            Task.due_date < now,
            Task.status != "completed",
            Task.status != "cancelled"
        ).all()

    def get_tasks_summary(self) -> dict:
        """Get summary of tasks by status"""
        all_tasks = self.db.query(Task).all()
        return {
            "total": len(all_tasks),
            "pending": len([t for t in all_tasks if t.status == "pending"]),
            "in_progress": len([t for t in all_tasks if t.status == "in_progress"]),
            "completed": len([t for t in all_tasks if t.status == "completed"]),
            "cancelled": len([t for t in all_tasks if t.status == "cancelled"]),
        }
