"""
Pydantic schemas for Smart Learning & Personalization
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Profile Schemas

class UserProfileCreate(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    preferred_language: str = "en"
    timezone: str = "UTC"
    notification_preferences: Dict[str, Any] = {}


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None
    notification_preferences: Optional[Dict[str, Any]] = None


class UserProfileResponse(BaseModel):
    id: int
    user_id: str
    name: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    preferred_language: str
    timezone: str
    notification_preferences: Dict[str, Any]
    voice_profile_id: Optional[str]
    total_tasks_created: int
    total_commands_executed: int
    total_voice_interactions: int
    created_at: datetime
    last_interaction: Optional[datetime]

    class Config:
        from_attributes = True


# User Habit Schemas

class UserHabitResponse(BaseModel):
    id: int
    user_id: str
    habit_type: str
    pattern_data: Dict[str, Any]
    frequency: int
    confidence: float
    time_of_day: Optional[str]
    day_of_week: Optional[str]
    last_occurrence: Optional[datetime]

    class Config:
        from_attributes = True


# Conversation Context Schemas

class ConversationContextCreate(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    user_message: str
    assistant_response: str
    intent: Optional[str] = None
    entities: Dict[str, Any] = {}
    language: str = "en"
    channel: str = "text"
    detected_mood: Optional[str] = None
    mood_confidence: Optional[float] = None
    voice_pitch: Optional[float] = None
    voice_energy: Optional[float] = None
    voice_rate: Optional[float] = None


class ConversationContextResponse(BaseModel):
    id: int
    user_id: str
    session_id: Optional[str]
    user_message: str
    assistant_response: str
    intent: Optional[str]
    entities: Dict[str, Any]
    language: str
    channel: str
    detected_mood: Optional[str]
    mood_confidence: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True


# Task Prediction Schemas

class TaskPredictionResponse(BaseModel):
    id: int
    predicted_task: str
    prediction_reason: Optional[str]
    confidence_score: float
    time_of_day: Optional[str]
    day_of_week: Optional[str]
    based_on_patterns: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class TaskPredictionFeedback(BaseModel):
    prediction_id: int
    accepted: bool
    user_id: str


# Morning Routine Schemas

class MorningRoutineCreate(BaseModel):
    user_id: str
    routine_name: str
    routine_items: List[Dict[str, Any]]
    preferred_time: str = "07:00"
    days_of_week: List[str] = ["monday", "tuesday", "wednesday", "thursday", "friday"]


class MorningRoutineUpdate(BaseModel):
    routine_name: Optional[str] = None
    routine_items: Optional[List[Dict[str, Any]]] = None
    preferred_time: Optional[str] = None
    days_of_week: Optional[List[str]] = None
    is_active: Optional[bool] = None


class MorningRoutineResponse(BaseModel):
    id: int
    user_id: str
    routine_name: Optional[str]
    routine_items: List[Dict[str, Any]]
    preferred_time: Optional[str]
    days_of_week: List[Any]
    auto_generated: bool
    based_on_habits: bool
    confidence: float
    times_executed: int
    last_executed: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


# Voice Profile Schemas

class VoiceProfileCreate(BaseModel):
    user_id: str
    profile_name: str
    description: Optional[str] = None


class VoiceProfileTrainingRequest(BaseModel):
    profile_id: str
    audio_samples: List[str] = Field(..., description="List of audio file paths for training")


class VoiceProfileResponse(BaseModel):
    id: int
    profile_id: str
    user_id: str
    profile_name: str
    description: Optional[str]
    training_samples: int
    recognition_accuracy: float
    is_active: bool
    is_primary: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Learning Insights Schemas

class LearningInsightsResponse(BaseModel):
    user_id: str
    habits_detected: int
    top_habits: List[Dict[str, Any]]
    predicted_tasks: List[TaskPredictionResponse]
    conversation_contexts: int
    mood_analysis: Dict[str, Any]
    personalization_score: float


class ContextAwareRequest(BaseModel):
    user_id: str
    message: str
    language: str = "en"
    channel: str = "text"
    session_id: Optional[str] = None
    include_context: bool = True
    context_window: int = 10  # Number of previous messages to consider


class ContextAwareResponse(BaseModel):
    response: str
    intent: str
    entities: Dict[str, Any]
    context_used: bool
    previous_contexts: List[Dict[str, Any]]
    suggested_actions: List[str]
    personalized: bool


class MoodDetectionRequest(BaseModel):
    user_id: str
    text: Optional[str] = None
    audio_file: Optional[str] = None
    voice_pitch: Optional[float] = None
    voice_energy: Optional[float] = None
    voice_rate: Optional[float] = None


class MoodDetectionResponse(BaseModel):
    detected_mood: str
    confidence: float
    mood_details: Dict[str, float]  # Breakdown of different moods
    recommendation: Optional[str]


class PersonalizedSuggestionRequest(BaseModel):
    user_id: str
    context: Optional[str] = None
    time_of_day: Optional[str] = None
    suggestion_type: str = "task"  # task, routine, command, etc.


class PersonalizedSuggestionResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    based_on: List[str]
    confidence_scores: List[float]


class VoiceRecognitionRequest(BaseModel):
    audio_file: str
    expected_users: Optional[List[str]] = None  # List of user_ids to check against


class VoiceRecognitionResponse(BaseModel):
    recognized_user_id: Optional[str]
    profile_id: Optional[str]
    confidence: float
    alternative_matches: List[Dict[str, Any]]
