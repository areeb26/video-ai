"""
Voice schemas for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class VoiceCommandRequest(BaseModel):
    """Schema for voice command request"""
    audio_file: Optional[str] = None
    text: Optional[str] = None  # Or provide text directly
    language: str = Field(default="en", pattern="^(en|ur)$")


class VoiceCommandResponse(BaseModel):
    """Schema for voice command response"""
    success: bool
    text: Optional[str] = None  # Recognized text
    response: Optional[str] = None  # Assistant response
    language: str
    audio_file: Optional[str] = None  # Response audio file path
    error: Optional[str] = None


class VoiceSpeakRequest(BaseModel):
    """Schema for text-to-speech request"""
    text: str = Field(..., min_length=1)
    language: str = Field(default="en", pattern="^(en|ur)$")
    save_to_file: bool = False
    filename: Optional[str] = None


class VoiceSpeakResponse(BaseModel):
    """Schema for text-to-speech response"""
    success: bool
    audio_file: Optional[str] = None
    error: Optional[str] = None


class VoiceListenerConfigRequest(BaseModel):
    """Schema for configuring voice listener"""
    wake_word_required: Optional[bool] = None
    continuous_mode: Optional[bool] = None
    response_enabled: Optional[bool] = None
    language: Optional[str] = Field(None, pattern="^(en|ur)$")
    speech_rate: Optional[int] = Field(None, ge=50, le=300)
    volume: Optional[float] = Field(None, ge=0.0, le=1.0)


class VoiceListenerStatusResponse(BaseModel):
    """Schema for voice listener status"""
    is_running: bool
    is_listening: bool
    continuous_mode: bool
    wake_word_required: bool
    response_enabled: bool
    command_count: int
    error_count: int
    default_language: str
    wake_word_stats: Dict[str, Any]


class VoiceWakeWordRequest(BaseModel):
    """Schema for wake word management"""
    wake_word: str = Field(..., min_length=2)
    language: Optional[str] = Field(None, pattern="^(en|ur)$")


class VoiceCalibrationRequest(BaseModel):
    """Schema for microphone calibration"""
    duration: int = Field(default=2, ge=1, le=10)


class VoiceDevicesResponse(BaseModel):
    """Schema for audio devices response"""
    devices: List[Dict[str, Any]]
    default_device: Optional[int] = None


class VoiceTestResponse(BaseModel):
    """Schema for voice test response"""
    success: bool
    message: str
    recognized_text: Optional[str] = None
