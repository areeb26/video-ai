"""
Task Model - Manages user tasks and reminders
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from ..core.database import Base


class Task(Base):
    """Task model for storing user tasks and reminders"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(10), default="en")  # en or ur

    # Status
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    priority = Column(String(20), default="medium")  # low, medium, high, urgent

    # Time tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Reminders
    reminder_enabled = Column(Boolean, default=False)
    reminder_time = Column(DateTime(timezone=True), nullable=True)
    reminder_sent = Column(Boolean, default=False)

    # Tags and categorization
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    category = Column(String(100), nullable=True)

    # N8N integration
    n8n_workflow_id = Column(String(100), nullable=True)
    n8n_execution_id = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<Task {self.id}: {self.title}>"
