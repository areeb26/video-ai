"""
File operation schemas for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FileOperationRequest(BaseModel):
    """Schema for file operation request"""
    operation_type: str = Field(..., pattern="^(create|read|edit|delete|move|copy|list)$")
    file_path: str = Field(..., min_length=1)
    new_path: Optional[str] = None
    content: Optional[str] = None
    language: str = Field(default="en", pattern="^(en|ur)$")


class FileOperationResponse(BaseModel):
    """Schema for file operation response"""
    id: int
    operation_type: str
    file_path: str
    new_path: Optional[str] = None
    file_name: str
    file_extension: Optional[str] = None
    file_size: Optional[int] = None
    content_preview: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
