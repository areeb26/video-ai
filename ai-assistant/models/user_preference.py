"""
User Preference Model - Stores user preferences and settings
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from ..core.database import Base


class UserPreference(Base):
    """User preferences model for storing user settings"""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)

    # User identification (for future multi-user support)
    user_id = Column(String(100), default="default_user", unique=True, index=True)

    # Language preferences
    preferred_language = Column(String(10), default="en")  # en or ur
    use_bilingual = Column(Boolean, default=True)

    # Notification preferences
    enable_notifications = Column(Boolean, default=True)
    enable_email_notifications = Column(Boolean, default=False)
    enable_task_reminders = Column(Boolean, default=True)

    # Workspace preferences
    default_workspace_dir = Column(String(500), nullable=True)
    auto_organize_files = Column(Boolean, default=False)

    # AI preferences
    ai_response_style = Column(String(50), default="friendly")  # friendly, formal, concise
    enable_suggestions = Column(Boolean, default=True)

    # N8N preferences
    default_n8n_webhook = Column(String(500), nullable=True)
    auto_trigger_workflows = Column(Boolean, default=False)

    # Custom settings (JSON field for extensibility)
    custom_settings = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<UserPreference {self.user_id}: {self.preferred_language}>"
