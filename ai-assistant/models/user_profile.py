"""
User Profile Model
Stores user preferences, habits, and personalization data
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float, Text
from sqlalchemy.sql import func
from .base import Base


class UserProfile(Base):
    """User profile for personalization"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200))
    email = Column(String(200))
    phone_number = Column(String(50))

    # Preferences
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    notification_preferences = Column(JSON, default={})

    # Voice Profile
    voice_profile_id = Column(String(100), unique=True, nullable=True)
    voice_features = Column(JSON, default={})  # Voice characteristics for recognition

    # Learning Data
    habits = Column(JSON, default={})  # Learned habits and patterns
    preferences = Column(JSON, default={})  # User preferences
    context_history = Column(JSON, default=[])  # Recent conversation context

    # Statistics
    total_tasks_created = Column(Integer, default=0)
    total_commands_executed = Column(Integer, default=0)
    total_voice_interactions = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_interaction = Column(DateTime(timezone=True), nullable=True)


class UserHabit(Base):
    """Stores learned user habits and patterns"""
    __tablename__ = "user_habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)

    # Habit Details
    habit_type = Column(String(100), nullable=False)  # task_creation, command_execution, etc.
    pattern_data = Column(JSON, nullable=False)  # Pattern details

    # Pattern Metrics
    frequency = Column(Integer, default=1)  # How often this pattern occurs
    confidence = Column(Float, default=0.5)  # Confidence score (0-1)
    last_occurrence = Column(DateTime(timezone=True))

    # Time-based patterns
    time_of_day = Column(String(20))  # morning, afternoon, evening, night
    day_of_week = Column(String(20))  # monday, tuesday, etc.

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ConversationContext(Base):
    """Stores conversation history for context-aware responses"""
    __tablename__ = "conversation_contexts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)
    session_id = Column(String(100), index=True)

    # Conversation Data
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    intent = Column(String(100))
    entities = Column(JSON, default={})

    # Context
    language = Column(String(10), default="en")
    channel = Column(String(50))  # voice, text, whatsapp, etc.

    # Mood Detection
    detected_mood = Column(String(50))  # happy, sad, neutral, angry, excited, etc.
    mood_confidence = Column(Float, default=0.0)

    # Voice Metrics (if from voice)
    voice_pitch = Column(Float, nullable=True)
    voice_energy = Column(Float, nullable=True)
    voice_rate = Column(Float, nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class TaskPrediction(Base):
    """Stores predicted tasks based on user patterns"""
    __tablename__ = "task_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)

    # Prediction Details
    predicted_task = Column(String(500), nullable=False)
    prediction_reason = Column(Text)  # Why this task was predicted
    confidence_score = Column(Float, nullable=False)  # 0-1

    # Context
    time_of_day = Column(String(20))
    day_of_week = Column(String(20))
    based_on_patterns = Column(JSON, default=[])  # Which patterns led to this prediction

    # Status
    shown_to_user = Column(Boolean, default=False)
    accepted_by_user = Column(Boolean, nullable=True)
    dismissed_by_user = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)


class MorningRoutine(Base):
    """Personalized morning routine suggestions"""
    __tablename__ = "morning_routines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)

    # Routine Details
    routine_name = Column(String(200))
    routine_items = Column(JSON, nullable=False)  # List of tasks/actions

    # Schedule
    preferred_time = Column(String(20))  # e.g., "07:00"
    days_of_week = Column(JSON, default=[])  # Which days this routine applies

    # Learning
    auto_generated = Column(Boolean, default=False)
    based_on_habits = Column(Boolean, default=False)
    confidence = Column(Float, default=0.5)

    # Usage Statistics
    times_executed = Column(Integer, default=0)
    times_modified = Column(Integer, default=0)
    last_executed = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)


class VoiceProfile(Base):
    """Voice recognition profiles for multiple users"""
    __tablename__ = "voice_profiles"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(100), index=True, nullable=False)

    # Profile Details
    profile_name = Column(String(200), nullable=False)
    description = Column(Text)

    # Voice Features (for recognition)
    voice_embeddings = Column(JSON, default={})  # Voice feature vectors
    pitch_range = Column(JSON, default={})  # min, max, average
    energy_range = Column(JSON, default={})
    speaking_rate = Column(Float)

    # Training Data
    training_samples = Column(Integer, default=0)
    last_training = Column(DateTime(timezone=True))

    # Accuracy Metrics
    recognition_accuracy = Column(Float, default=0.0)
    false_positive_rate = Column(Float, default=0.0)

    # Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
