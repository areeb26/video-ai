"""
Assistant schemas for natural language processing
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class AssistantRequest(BaseModel):
    """Schema for assistant request (natural language)"""
    message: str = Field(..., min_length=1)
    language: str = Field(default="en", pattern="^(en|ur)$")
    context: Optional[Dict[str, Any]] = None


class AssistantResponse(BaseModel):
    """Schema for assistant response"""
    message: str
    language: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    success: bool
    metadata: Optional[Dict[str, Any]] = None
