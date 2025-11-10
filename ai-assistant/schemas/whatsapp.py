"""
WhatsApp schemas for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class WhatsAppMessageRequest(BaseModel):
    """Schema for sending WhatsApp message"""
    number: str = Field(..., min_length=10, max_length=20)
    message: str = Field(..., min_length=1)
    language: str = Field(default="en", pattern="^(en|ur)$")
    method: str = Field(default="selenium", pattern="^(selenium|simple)$")


class WhatsAppFileRequest(BaseModel):
    """Schema for sending WhatsApp file"""
    number: str = Field(..., min_length=10, max_length=20)
    file_path: str = Field(..., min_length=1)
    caption: str = Field(default="")
    language: str = Field(default="en", pattern="^(en|ur)$")


class WhatsAppScheduleRequest(BaseModel):
    """Schema for scheduling WhatsApp message"""
    number: str = Field(..., min_length=10, max_length=20)
    message: str = Field(..., min_length=1)
    send_at: Optional[datetime] = None
    delay_minutes: int = Field(default=0, ge=0)
    delay_hours: int = Field(default=0, ge=0)
    delay_days: int = Field(default=0, ge=0)
    language: str = Field(default="en", pattern="^(en|ur)$")


class WhatsAppMessageResponse(BaseModel):
    """Schema for WhatsApp message response"""
    success: bool
    message: str
    message_id: Optional[str] = None
    error: Optional[str] = None


class WhatsAppAuthRequest(BaseModel):
    """Schema for adding authorized number"""
    number: str = Field(..., min_length=10, max_length=20)


class WhatsAppSessionResponse(BaseModel):
    """Schema for session status response"""
    is_logged_in: bool
    session_valid: bool
    session_stats: Dict[str, Any]
    queue_stats: Dict[str, Any]
