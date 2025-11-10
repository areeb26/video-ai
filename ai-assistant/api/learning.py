"""
Smart Learning & Personalization API
Endpoints for learning, prediction, and personalization features
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..schemas.learning import *
from ..learning import (
    PatternRecognizer,
    HabitLearner,
    TaskPredictor,
    ContextManager,
    MoodDetector,
    VoiceRecognizer,
    SuggestionEngine
)

router = APIRouter(prefix="/learning", tags=["Smart Learning"])


# User Profile Endpoints

@router.post("/profile", response_model=UserProfileResponse)
async def create_user_profile(
    profile: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new user profile"""
    from ..models.user_profile import UserProfile

    # Check if profile already exists
    existing = db.query(UserProfile).filter(
        UserProfile.user_id == profile.user_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User profile already exists")

    new_profile = UserProfile(**profile.model_dump())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user profile"""
    from ..models.user_profile import UserProfile

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    return profile


@router.put("/profile/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: str,
    profile_update: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update user profile"""
    from ..models.user_profile import UserProfile

    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Update fields
    for field, value in profile_update.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile


# Pattern Recognition & Habit Learning

@router.post("/habits/{user_id}/learn")
async def learn_user_habits(
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Learn habits from user patterns"""
    habit_learner = HabitLearner(db)

    def learn_task():
        new_habits = habit_learner.learn_habits(user_id)
        return new_habits

    background_tasks.add_task(learn_task)

    return {
        "message": "Habit learning started in background",
        "user_id": user_id
    }


@router.get("/habits/{user_id}", response_model=List[UserHabitResponse])
async def get_user_habits(
    user_id: str,
    habit_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get learned habits for a user"""
    from ..models.user_profile import UserHabit

    query = db.query(UserHabit).filter(UserHabit.user_id == user_id)

    if habit_type:
        query = query.filter(UserHabit.habit_type == habit_type)

    habits = query.order_by(UserHabit.confidence.desc()).all()

    return habits


@router.get("/habits/{user_id}/insights")
async def get_habit_insights(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get insights from learned habits"""
    habit_learner = HabitLearner(db)
    insights = habit_learner.get_habit_insights(user_id)

    return insights


# Task Prediction

@router.post("/predict/tasks/{user_id}")
async def predict_tasks(
    user_id: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Predict tasks user might want to create"""
    predictor = TaskPredictor(db)
    predictions = predictor.predict_tasks(user_id, limit=limit)

    return {
        "user_id": user_id,
        "predictions": predictions,
        "timestamp": datetime.now()
    }


@router.get("/predict/tasks/{user_id}/stored", response_model=List[TaskPredictionResponse])
async def get_stored_predictions(
    user_id: str,
    include_dismissed: bool = False,
    db: Session = Depends(get_db)
):
    """Get stored task predictions"""
    predictor = TaskPredictor(db)
    predictions = predictor.get_predictions_for_user(user_id, include_dismissed)

    from ..models.user_profile import TaskPrediction

    pred_models = db.query(TaskPrediction).filter(
        TaskPrediction.user_id == user_id,
        TaskPrediction.shown_to_user == False
    ).order_by(TaskPrediction.confidence_score.desc()).all()

    return pred_models


@router.post("/predict/tasks/feedback")
async def task_prediction_feedback(
    feedback: TaskPredictionFeedback,
    db: Session = Depends(get_db)
):
    """Provide feedback on task prediction"""
    predictor = TaskPredictor(db)

    if feedback.accepted:
        success = predictor.accept_prediction(feedback.user_id, feedback.prediction_id)
    else:
        success = predictor.dismiss_prediction(feedback.user_id, feedback.prediction_id)

    if not success:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return {
        "message": "Feedback recorded",
        "prediction_id": feedback.prediction_id,
        "accepted": feedback.accepted
    }


@router.get("/predict/tasks/{user_id}/accuracy")
async def get_prediction_accuracy(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get prediction accuracy metrics"""
    predictor = TaskPredictor(db)
    accuracy = predictor.get_prediction_accuracy(user_id)

    return accuracy


# Context-Aware Conversations

@router.post("/context/save")
async def save_conversation_context(
    context: ConversationContextCreate,
    db: Session = Depends(get_db)
):
    """Save conversation context"""
    context_manager = ContextManager(db)

    context_id = context_manager.save_context(
        user_id=context.user_id,
        user_message=context.user_message,
        assistant_response=context.assistant_response,
        intent=context.intent,
        entities=context.entities,
        language=context.language,
        channel=context.channel,
        session_id=context.session_id,
        mood_data={
            'mood': context.detected_mood,
            'confidence': context.mood_confidence,
            'pitch': context.voice_pitch,
            'energy': context.voice_energy,
            'rate': context.voice_rate
        } if context.detected_mood else None
    )

    return {
        "context_id": context_id,
        "message": "Context saved successfully"
    }


@router.get("/context/{user_id}", response_model=List[ConversationContextResponse])
async def get_conversation_context(
    user_id: str,
    limit: int = 10,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get recent conversation context"""
    context_manager = ContextManager(db)
    contexts = context_manager.get_recent_context(user_id, limit, session_id)

    from ..models.user_profile import ConversationContext

    context_models = db.query(ConversationContext).filter(
        ConversationContext.user_id == user_id
    ).order_by(ConversationContext.timestamp.desc()).limit(limit).all()

    return context_models


@router.post("/context/aware", response_model=ContextAwareResponse)
async def get_context_aware_response(
    request: ContextAwareRequest,
    db: Session = Depends(get_db)
):
    """Get context-aware response suggestions"""
    context_manager = ContextManager(db)

    intent, relevant_contexts, suggestions = context_manager.get_contextual_response(
        user_id=request.user_id,
        current_message=request.message,
        language=request.language,
        session_id=request.session_id
    )

    return {
        "response": "Context-aware processing complete",
        "intent": intent,
        "entities": {},
        "context_used": len(relevant_contexts) > 0,
        "previous_contexts": relevant_contexts,
        "suggested_actions": suggestions,
        "personalized": True
    }


@router.get("/context/{user_id}/summary")
async def get_conversation_summary(
    user_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get conversation summary"""
    context_manager = ContextManager(db)
    summary = context_manager.get_conversation_summary(user_id, days)

    return summary


@router.get("/context/{user_id}/mood-history")
async def get_mood_history(
    user_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get mood history"""
    context_manager = ContextManager(db)
    mood_history = context_manager.get_mood_history(user_id, days)

    return {
        "user_id": user_id,
        "mood_history": mood_history,
        "days": days
    }


# Mood Detection

@router.post("/mood/detect", response_model=MoodDetectionResponse)
async def detect_mood(
    request: MoodDetectionRequest
):
    """Detect mood from text and/or voice"""
    mood_detector = MoodDetector()

    result = mood_detector.detect_mood_combined(
        text=request.text,
        language="en",  # Could be extracted from text
        pitch=request.voice_pitch,
        energy=request.voice_energy,
        rate=request.voice_rate,
        audio_file=request.audio_file
    )

    recommendation = mood_detector.get_mood_recommendation(
        result['mood'],
        result['confidence']
    )

    return {
        "detected_mood": result['mood'],
        "confidence": result['confidence'],
        "mood_details": result.get('mood_breakdown', {}),
        "recommendation": recommendation
    }


@router.post("/mood/analyze-trend")
async def analyze_mood_trend(
    user_id: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Analyze mood trend over time"""
    context_manager = ContextManager(db)
    mood_history = context_manager.get_mood_history(user_id, days)

    mood_detector = MoodDetector()
    trend_analysis = mood_detector.analyze_mood_trend(mood_history)

    return {
        "user_id": user_id,
        "trend_analysis": trend_analysis,
        "mood_history_count": len(mood_history)
    }


# Voice Profile Recognition

@router.post("/voice-profile", response_model=VoiceProfileResponse)
async def create_voice_profile(
    profile: VoiceProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new voice profile"""
    voice_recognizer = VoiceRecognizer(db)

    profile_id = voice_recognizer.create_voice_profile(
        user_id=profile.user_id,
        profile_name=profile.profile_name,
        description=profile.description
    )

    return voice_recognizer.get_voice_profile(profile_id)


@router.post("/voice-profile/train")
async def train_voice_profile(
    training: VoiceProfileTrainingRequest,
    db: Session = Depends(get_db)
):
    """Train voice profile with audio samples"""
    voice_recognizer = VoiceRecognizer(db)

    success = voice_recognizer.train_voice_profile(
        profile_id=training.profile_id,
        audio_samples=training.audio_samples
    )

    if not success:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    return {
        "message": "Voice profile trained successfully",
        "profile_id": training.profile_id,
        "samples_used": len(training.audio_samples)
    }


@router.post("/voice-profile/recognize", response_model=VoiceRecognitionResponse)
async def recognize_user_from_voice(
    request: VoiceRecognitionRequest,
    db: Session = Depends(get_db)
):
    """Recognize user from voice sample"""
    voice_recognizer = VoiceRecognizer(db)

    user_id, profile_id, confidence, alternatives = voice_recognizer.recognize_user_from_voice(
        audio_file=request.audio_file,
        expected_users=request.expected_users
    )

    return {
        "recognized_user_id": user_id,
        "profile_id": profile_id,
        "confidence": confidence,
        "alternative_matches": alternatives
    }


@router.get("/voice-profile/{user_id}/profiles", response_model=List[VoiceProfileResponse])
async def get_user_voice_profiles(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all voice profiles for a user"""
    voice_recognizer = VoiceRecognizer(db)
    profiles = voice_recognizer.get_user_profiles(user_id)

    from ..models.user_profile import VoiceProfile

    profile_models = db.query(VoiceProfile).filter(
        VoiceProfile.user_id == user_id
    ).order_by(VoiceProfile.is_primary.desc()).all()

    return profile_models


@router.delete("/voice-profile/{profile_id}")
async def delete_voice_profile(
    profile_id: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Delete a voice profile"""
    voice_recognizer = VoiceRecognizer(db)

    success = voice_recognizer.delete_voice_profile(profile_id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Voice profile not found")

    return {
        "message": "Voice profile deleted successfully",
        "profile_id": profile_id
    }


# Personalized Suggestions

@router.post("/suggestions/{user_id}", response_model=PersonalizedSuggestionResponse)
async def get_personalized_suggestions(
    user_id: str,
    request: PersonalizedSuggestionRequest,
    db: Session = Depends(get_db)
):
    """Get personalized suggestions"""
    suggestion_engine = SuggestionEngine(db)

    suggestions = suggestion_engine.get_personalized_suggestions(
        user_id=user_id,
        context=request.context,
        limit=5
    )

    all_suggestions = []
    confidence_scores = []
    based_on = suggestions.get('based_on', [])

    # Collect all suggestions with confidence
    for suggestion_list in [suggestions['tasks'], suggestions['routines'], suggestions['commands'], suggestions['responses']]:
        for s in suggestion_list:
            all_suggestions.append(s)
            confidence_scores.append(s.get('confidence', 0.5))

    return {
        "suggestions": all_suggestions,
        "based_on": based_on,
        "confidence_scores": confidence_scores
    }


@router.get("/suggestions/{user_id}/morning-routine")
async def get_morning_routine_suggestion(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get personalized morning routine suggestion"""
    suggestion_engine = SuggestionEngine(db)
    routine = suggestion_engine.get_morning_routine_suggestion(user_id)

    return routine


@router.get("/suggestions/{user_id}/time-based")
async def get_time_based_suggestions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get auto-suggestions based on current time"""
    suggestion_engine = SuggestionEngine(db)
    suggestions = suggestion_engine.get_auto_suggestions_based_on_time(user_id)

    return {
        "user_id": user_id,
        "suggestions": suggestions,
        "timestamp": datetime.now()
    }


# Morning Routines

@router.post("/routines", response_model=MorningRoutineResponse)
async def create_morning_routine(
    routine: MorningRoutineCreate,
    db: Session = Depends(get_db)
):
    """Create a morning routine"""
    from ..models.user_profile import MorningRoutine

    new_routine = MorningRoutine(**routine.model_dump())
    db.add(new_routine)
    db.commit()
    db.refresh(new_routine)

    return new_routine


@router.get("/routines/{user_id}", response_model=List[MorningRoutineResponse])
async def get_user_routines(
    user_id: str,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get user's morning routines"""
    from ..models.user_profile import MorningRoutine

    query = db.query(MorningRoutine).filter(
        MorningRoutine.user_id == user_id
    )

    if active_only:
        query = query.filter(MorningRoutine.is_active == True)

    routines = query.order_by(MorningRoutine.created_at.desc()).all()

    return routines


@router.put("/routines/{routine_id}", response_model=MorningRoutineResponse)
async def update_morning_routine(
    routine_id: int,
    routine_update: MorningRoutineUpdate,
    db: Session = Depends(get_db)
):
    """Update a morning routine"""
    from ..models.user_profile import MorningRoutine

    routine = db.query(MorningRoutine).filter(
        MorningRoutine.id == routine_id
    ).first()

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    # Update fields
    for field, value in routine_update.model_dump(exclude_unset=True).items():
        setattr(routine, field, value)

    routine.times_modified += 1
    db.commit()
    db.refresh(routine)

    return routine


# Learning Insights

@router.get("/insights/{user_id}", response_model=LearningInsightsResponse)
async def get_learning_insights(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive learning insights for user"""
    habit_learner = HabitLearner(db)
    task_predictor = TaskPredictor(db)
    context_manager = ContextManager(db)

    # Get insights
    habit_insights = habit_learner.get_habit_insights(user_id)
    predictions = task_predictor.get_predictions_for_user(user_id)
    conversation_summary = context_manager.get_conversation_summary(user_id)
    mood_history = context_manager.get_mood_history(user_id)

    # Analyze mood
    mood_detector = MoodDetector()
    mood_analysis = mood_detector.analyze_mood_trend(mood_history)

    # Calculate personalization score (0-1)
    personalization_score = min(
        (habit_insights['total_habits'] / 20) * 0.4 +  # Habits (max 20)
        (len(predictions) / 10) * 0.3 +  # Predictions (max 10)
        (conversation_summary['total_conversations'] / 100) * 0.3,  # Conversations (max 100)
        1.0
    )

    from ..models.user_profile import TaskPrediction

    stored_predictions = db.query(TaskPrediction).filter(
        TaskPrediction.user_id == user_id
    ).order_by(TaskPrediction.confidence_score.desc()).limit(5).all()

    return {
        "user_id": user_id,
        "habits_detected": habit_insights['total_habits'],
        "top_habits": habit_insights['strongest_habits'],
        "predicted_tasks": stored_predictions,
        "conversation_contexts": conversation_summary['total_conversations'],
        "mood_analysis": mood_analysis,
        "personalization_score": personalization_score
    }


@router.get("/health")
async def learning_health_check():
    """Health check for learning features"""
    return {
        "status": "healthy",
        "features": [
            "Pattern Recognition",
            "Habit Learning",
            "Task Prediction",
            "Context-Aware Conversations",
            "Mood Detection",
            "Voice Profile Recognition",
            "Personalized Suggestions"
        ],
        "version": "1.0.0"
    }
