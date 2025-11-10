"""
N8N workflow schemas for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class N8NWorkflowRequest(BaseModel):
    """Schema for N8N workflow execution request"""
    workflow_name: str = Field(..., min_length=1, max_length=200)
    webhook_url: str = Field(..., min_length=1)
    payload: Optional[Dict[str, Any]] = None
    triggered_by: Optional[str] = None
    language: str = Field(default="en", pattern="^(en|ur)$")
    auto_retry: bool = False
    max_retries: int = Field(default=3, ge=0, le=10)


class N8NWorkflowResponse(BaseModel):
    """Schema for N8N workflow execution response"""
    id: int
    workflow_id: Optional[str] = None
    workflow_name: str
    webhook_url: str
    execution_id: Optional[str] = None
    status: str
    request_payload: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[int] = None
    retry_count: int

    class Config:
        from_attributes = True
