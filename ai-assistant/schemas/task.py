"""
Task schemas for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    language: str = Field(default="en", pattern="^(en|ur)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    due_date: Optional[datetime] = None
    reminder_enabled: bool = False
    reminder_time: Optional[datetime] = None
    tags: Optional[str] = None
    category: Optional[str] = None


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|cancelled)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    due_date: Optional[datetime] = None
    reminder_enabled: Optional[bool] = None
    reminder_time: Optional[datetime] = None
    tags: Optional[str] = None
    category: Optional[str] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    reminder_sent: bool
    n8n_workflow_id: Optional[str] = None
    n8n_execution_id: Optional[str] = None

    class Config:
        from_attributes = True
