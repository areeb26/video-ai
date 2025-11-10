"""
Command schemas for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommandRequest(BaseModel):
    """Schema for command execution request"""
    command: str = Field(..., min_length=1)
    command_type: str = Field(..., pattern="^(system|file|n8n|task|query)$")
    language: str = Field(default="en", pattern="^(en|ur)$")
    user_input: Optional[str] = None


class CommandResponse(BaseModel):
    """Schema for command execution response"""
    id: int
    command: str
    command_type: str
    status: str
    output: Optional[str] = None
    error_message: Optional[str] = None
    is_safe: bool
    was_blocked: bool
    created_at: datetime
    executed_at: Optional[datetime] = None
    execution_time: Optional[int] = None

    class Config:
        from_attributes = True
