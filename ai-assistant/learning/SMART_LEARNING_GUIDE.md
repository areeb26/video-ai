# Smart Learning & Personalization - Complete Guide

Comprehensive guide for the AI Assistant's Smart Learning & Personalization features.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Getting Started](#getting-started)
4. [User Profiles](#user-profiles)
5. [Habit Learning](#habit-learning)
6. [Task Prediction](#task-prediction)
7. [Context-Aware Conversations](#context-aware-conversations)
8. [Mood Detection](#mood-detection)
9. [Voice Profile Recognition](#voice-profile-recognition)
10. [Personalized Suggestions](#personalized-suggestions)
11. [Morning Routines](#morning-routines)
12. [API Reference](#api-reference)
13. [Examples](#examples)

---

## Overview

The Smart Learning & Personalization system makes your AI Assistant truly personal by:

- **Learning your habits** - Automatically detects patterns in how you work
- **Predicting your needs** - Suggests tasks before you ask
- **Remembering context** - Understands conversation history
- **Detecting mood** - Adapts responses based on your emotional state
- **Recognizing your voice** - Identifies different users by voice
- **Personalizing suggestions** - Tailored recommendations based on your patterns

---

## Features

### ✅ Habit Learning
- Detects recurring patterns in task creation
- Learns command usage habits
- Identifies time-based routines
- Tracks language and channel preferences

### ✅ Task Prediction
- Predicts next tasks based on history
- Suggests tasks at appropriate times
- Learns from your acceptance/rejection
- Improves accuracy over time

### ✅ Context-Aware Conversations
- Remembers previous conversations
- Understands follow-up questions
- Provides relevant suggestions
- Maintains conversation context

### ✅ Mood Detection
- Analyzes text for emotional indicators
- Detects mood from voice tone
- Tracks mood trends over time
- Adapts responses to your mood

### ✅ Voice Profile Recognition
- Creates unique voice profiles
- Recognizes users by voice
- Supports multiple users
- Improves with usage

### ✅ Personalized Suggestions
- Task suggestions based on habits
- Command suggestions based on time
- Response suggestions in conversations
- Morning routine recommendations

---

## Getting Started

### Prerequisites

The Smart Learning system is automatically enabled with the AI Assistant. Ensure:

1. **AI Assistant is running**
   ```bash
   cd ai-assistant
   python main.py
   ```

2. **Configuration is set** (in `.env`)
   ```env
   LEARNING_ENABLED=True
   LEARNING_AUTO_LEARN=True
   ```

### Initial Setup

**Step 1: Create User Profile**

```bash
curl -X POST http://localhost:8001/api/v1/learning/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "name": "John Doe",
    "preferred_language": "en",
    "timezone": "America/New_York"
  }'
```

**Step 2: Start Using the Assistant**

The system learns automatically as you:
- Create tasks
- Execute commands
- Have conversations
- Use voice commands

**Step 3: Check Learning Progress**

```bash
curl http://localhost:8001/api/v1/learning/insights/user123
```

---

## User Profiles

### Create Profile

```bash
curl -X POST http://localhost:8001/api/v1/learning/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+1234567890",
    "preferred_language": "en",
    "timezone": "UTC"
  }'
```

### Get Profile

```bash
curl http://localhost:8001/api/v1/learning/profile/user123
```

### Update Profile

```bash
curl -X PUT http://localhost:8001/api/v1/learning/profile/user123 \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_language": "ur",
    "timezone": "Asia/Karachi"
  }'
```

---

## Habit Learning

### How It Works

The system automatically:
1. **Monitors your actions** - Tasks, commands, conversations
2. **Detects patterns** - Recurring behaviors and preferences
3. **Calculates confidence** - How sure it is about each pattern
4. **Saves as habits** - Patterns above threshold become habits

### Trigger Learning

```bash
curl -X POST http://localhost:8001/api/v1/learning/habits/user123/learn
```

### View Learned Habits

```bash
# All habits
curl http://localhost:8001/api/v1/learning/habits/user123

# Specific type
curl "http://localhost:8001/api/v1/learning/habits/user123?habit_type=recurring_task"
```

### Get Habit Insights

```bash
curl http://localhost:8001/api/v1/learning/habits/user123/insights
```

**Response:**
```json
{
  "total_habits": 15,
  "habit_categories": {
    "recurring_task": 5,
    "command_usage": 4,
    "language_preference": 2,
    "time_based": 4
  },
  "strongest_habits": [
    {
      "habit_type": "recurring_task",
      "confidence": 0.92,
      "pattern_data": {
        "keyword": "meeting",
        "description": "User frequently creates meeting-related tasks"
      }
    }
  ]
}
```

### Habit Types

- **recurring_task** - Tasks you create repeatedly
- **command_usage** - Commands you run frequently
- **time_based** - Actions at specific times
- **language_preference** - Your preferred language
- **channel_preference** - Preferred communication channel

---

## Task Prediction

### Get Predictions

```bash
curl -X POST http://localhost:8001/api/v1/learning/predict/tasks/user123
```

**Response:**
```json
{
  "user_id": "user123",
  "predictions": [
    {
      "task": "Weekly team meeting",
      "reason": "You usually create this task on Monday mornings",
      "confidence": 0.85,
      "time_of_day": "morning",
      "patterns": [{"type": "weekly_pattern"}]
    },
    {
      "task": "Review emails",
      "reason": "Common task in the morning",
      "confidence": 0.78
    }
  ]
}
```

### Provide Feedback

**Accept Prediction:**
```bash
curl -X POST http://localhost:8001/api/v1/learning/predict/tasks/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": 123,
    "accepted": true,
    "user_id": "user123"
  }'
```

**Dismiss Prediction:**
```bash
curl -X POST http://localhost:8001/api/v1/learning/predict/tasks/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "prediction_id": 124,
    "accepted": false,
    "user_id": "user123"
  }'
```

### Check Accuracy

```bash
curl http://localhost:8001/api/v1/learning/predict/tasks/user123/accuracy
```

**Response:**
```json
{
  "total_predictions": 50,
  "accepted": 38,
  "dismissed": 12,
  "accuracy": 0.76,
  "acceptance_rate": 0.76
}
```

---

## Context-Aware Conversations

### How It Works

The assistant:
1. **Saves conversation history**
2. **Analyzes context** when you ask follow-up questions
3. **Provides relevant suggestions** based on previous exchanges
4. **Remembers entities** mentioned earlier

### Save Context

```bash
curl -X POST http://localhost:8001/api/v1/learning/context/save \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "user_message": "Create a task to call the dentist",
    "assistant_response": "Task created: Call the dentist",
    "intent": "create_task",
    "language": "en",
    "channel": "text"
  }'
```

### Get Context

```bash
curl "http://localhost:8001/api/v1/learning/context/user123?limit=10"
```

### Context-Aware Response

```bash
curl -X POST http://localhost:8001/api/v1/learning/context/aware \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Set a reminder for it",
    "language": "en",
    "include_context": true
  }'
```

**Response:**
```json
{
  "response": "Context-aware processing complete",
  "intent": "contextual_reference",
  "context_used": true,
  "previous_contexts": [
    {
      "user_message": "Create a task to call the dentist",
      "assistant_response": "Task created: Call the dentist",
      "intent": "create_task"
    }
  ],
  "suggested_actions": [
    "Set reminder for this task",
    "Add more details"
  ]
}
```

### Conversation Summary

```bash
curl "http://localhost:8001/api/v1/learning/context/user123/summary?days=7"
```

**Response:**
```json
{
  "total_conversations": 45,
  "languages": {"en": 40, "ur": 5},
  "channels": {"text": 30, "voice": 15},
  "intents": {
    "create_task": 20,
    "list_tasks": 10,
    "send_whatsapp": 5
  },
  "avg_conversations_per_day": 6.4
}
```

---

## Mood Detection

### Detect from Text

```bash
curl -X POST http://localhost:8001/api/v1/learning/mood/detect \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "text": "I am feeling great today! Very excited about the new project."
  }'
```

**Response:**
```json
{
  "detected_mood": "excited",
  "confidence": 0.87,
  "mood_details": {
    "happy": 0.4,
    "excited": 0.87,
    "neutral": 0.2
  },
  "recommendation": "That's wonderful energy! Let's channel that into getting things done."
}
```

### Detect from Voice

```bash
curl -X POST http://localhost:8001/api/v1/learning/mood/detect \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "voice_pitch": 220,
    "voice_energy": 0.8,
    "voice_rate": 160
  }'
```

### Detect from Both

```bash
curl -X POST http://localhost:8001/api/v1/learning/mood/detect \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "text": "I am not sure about this",
    "voice_pitch": 150,
    "voice_energy": 0.3,
    "voice_rate": 110
  }'
```

### Mood History

```bash
curl "http://localhost:8001/api/v1/learning/context/user123/mood-history?days=7"
```

### Analyze Mood Trend

```bash
curl -X POST "http://localhost:8001/api/v1/learning/mood/analyze-trend?user_id=user123&days=7"
```

**Response:**
```json
{
  "trend": "improving",
  "avg_confidence": 0.82,
  "dominant_mood": "happy",
  "mood_stability": 0.75,
  "mood_distribution": {
    "happy": 15,
    "neutral": 8,
    "excited": 5,
    "anxious": 2
  }
}
```

---

## Voice Profile Recognition

### Create Voice Profile

```bash
curl -X POST http://localhost:8001/api/v1/learning/voice-profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "profile_name": "John Work Profile",
    "description": "Primary work voice profile"
  }'
```

### Train Profile

```bash
curl -X POST http://localhost:8001/api/v1/learning/voice-profile/train \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "vp_abc123",
    "audio_samples": [
      "/path/to/sample1.wav",
      "/path/to/sample2.wav",
      "/path/to/sample3.wav"
    ]
  }'
```

### Recognize User

```bash
curl -X POST http://localhost:8001/api/v1/learning/voice-profile/recognize \
  -H "Content-Type: application/json" \
  -d '{
    "audio_file": "/path/to/test_audio.wav",
    "expected_users": ["user123", "user456"]
  }'
```

**Response:**
```json
{
  "recognized_user_id": "user123",
  "profile_id": "vp_abc123",
  "confidence": 0.89,
  "alternative_matches": [
    {
      "user_id": "user456",
      "confidence": 0.45
    }
  ]
}
```

### Get User Profiles

```bash
curl http://localhost:8001/api/v1/learning/voice-profile/user123/profiles
```

### Delete Profile

```bash
curl -X DELETE "http://localhost:8001/api/v1/learning/voice-profile/vp_abc123?user_id=user123"
```

---

## Personalized Suggestions

### Get All Suggestions

```bash
curl -X POST http://localhost:8001/api/v1/learning/suggestions/user123 \
  -H "Content-Type: application/json" \
  -d '{
    "suggestion_type": "task",
    "context": "morning routine"
  }'
```

**Response:**
```json
{
  "suggestions": [
    {
      "type": "task",
      "content": "Review today's meetings",
      "reason": "You usually do this in the morning",
      "confidence": 0.85,
      "action": "create_task"
    },
    {
      "type": "routine",
      "content": "Start morning routine",
      "reason": "It's 7 AM",
      "confidence": 0.8
    }
  ],
  "based_on": ["task_history", "time_patterns", "morning_habits"]
}
```

### Morning Routine Suggestions

```bash
curl http://localhost:8001/api/v1/learning/suggestions/user123/morning-routine
```

**Response:**
```json
{
  "has_routine": false,
  "suggestion": "Create a morning routine",
  "suggested_routine": {
    "name": "Personalized Morning Routine",
    "items": [
      {"task": "Check emails", "time": "07:00", "duration": 15},
      {"task": "Review calendar", "time": "07:15", "duration": 10},
      {"task": "Plan priorities", "time": "07:25", "duration": 15}
    ],
    "confidence": 0.75
  }
}
```

### Time-Based Suggestions

```bash
curl http://localhost:8001/api/v1/learning/suggestions/user123/time-based
```

---

## Morning Routines

### Create Routine

```bash
curl -X POST http://localhost:8001/api/v1/learning/routines \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "routine_name": "My Morning Routine",
    "routine_items": [
      {"task": "Check emails", "time": "07:00"},
      {"task": "Review tasks", "time": "07:20"},
      {"task": "Morning standup", "time": "09:00"}
    ],
    "preferred_time": "07:00",
    "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"]
  }'
```

### Get Routines

```bash
curl http://localhost:8001/api/v1/learning/routines/user123
```

### Update Routine

```bash
curl -X PUT http://localhost:8001/api/v1/learning/routines/123 \
  -H "Content-Type: application/json" \
  -d '{
    "routine_name": "Updated Morning Routine",
    "is_active": true
  }'
```

---

## API Reference

### Endpoints Overview

**User Profiles:**
- `POST /api/v1/learning/profile` - Create profile
- `GET /api/v1/learning/profile/{user_id}` - Get profile
- `PUT /api/v1/learning/profile/{user_id}` - Update profile

**Habit Learning:**
- `POST /api/v1/learning/habits/{user_id}/learn` - Trigger learning
- `GET /api/v1/learning/habits/{user_id}` - Get habits
- `GET /api/v1/learning/habits/{user_id}/insights` - Get insights

**Task Prediction:**
- `POST /api/v1/learning/predict/tasks/{user_id}` - Get predictions
- `POST /api/v1/learning/predict/tasks/feedback` - Provide feedback
- `GET /api/v1/learning/predict/tasks/{user_id}/accuracy` - Check accuracy

**Context:**
- `POST /api/v1/learning/context/save` - Save context
- `GET /api/v1/learning/context/{user_id}` - Get context
- `POST /api/v1/learning/context/aware` - Context-aware response
- `GET /api/v1/learning/context/{user_id}/summary` - Get summary

**Mood Detection:**
- `POST /api/v1/learning/mood/detect` - Detect mood
- `POST /api/v1/learning/mood/analyze-trend` - Analyze trend
- `GET /api/v1/learning/context/{user_id}/mood-history` - Get history

**Voice Profiles:**
- `POST /api/v1/learning/voice-profile` - Create profile
- `POST /api/v1/learning/voice-profile/train` - Train profile
- `POST /api/v1/learning/voice-profile/recognize` - Recognize user
- `GET /api/v1/learning/voice-profile/{user_id}/profiles` - Get profiles
- `DELETE /api/v1/learning/voice-profile/{profile_id}` - Delete profile

**Suggestions:**
- `POST /api/v1/learning/suggestions/{user_id}` - Get suggestions
- `GET /api/v1/learning/suggestions/{user_id}/morning-routine` - Morning routine
- `GET /api/v1/learning/suggestions/{user_id}/time-based` - Time-based

**Routines:**
- `POST /api/v1/learning/routines` - Create routine
- `GET /api/v1/learning/routines/{user_id}` - Get routines
- `PUT /api/v1/learning/routines/{routine_id}` - Update routine

**Insights:**
- `GET /api/v1/learning/insights/{user_id}` - Get all insights
- `GET /api/v1/learning/health` - Health check

---

## Examples

### Example 1: Complete User Setup

```bash
# 1. Create user profile
curl -X POST http://localhost:8001/api/v1/learning/profile \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john_doe",
    "name": "John Doe",
    "preferred_language": "en",
    "timezone": "America/New_York"
  }'

# 2. Use the assistant (creates tasks, executes commands)
# ... user interaction ...

# 3. Trigger learning
curl -X POST http://localhost:8001/api/v1/learning/habits/john_doe/learn

# 4. Get predictions
curl -X POST http://localhost:8001/api/v1/learning/predict/tasks/john_doe

# 5. Get insights
curl http://localhost:8001/api/v1/learning/insights/john_doe
```

### Example 2: Context-Aware Conversation

```python
import requests

base_url = "http://localhost:8001/api/v1"

# User: "Create a task to review the proposal"
response = requests.post(f"{base_url}/assistant", json={
    "message": "Create a task to review the proposal",
    "user_id": "john_doe",
    "language": "en"
})

# Save context
requests.post(f"{base_url}/learning/context/save", json={
    "user_id": "john_doe",
    "user_message": "Create a task to review the proposal",
    "assistant_response": response.json()['response'],
    "intent": "create_task",
    "language": "en"
})

# User: "Set a reminder for it tomorrow"
context_response = requests.post(f"{base_url}/learning/context/aware", json={
    "user_id": "john_doe",
    "message": "Set a reminder for it tomorrow",
    "language": "en"
})

print(context_response.json())
# Will understand "it" refers to the proposal task
```

### Example 3: Mood-Aware Responses

```python
import requests

base_url = "http://localhost:8001/api/v1"

# Detect mood
mood = requests.post(f"{base_url}/learning/mood/detect", json={
    "user_id": "john_doe",
    "text": "I'm feeling overwhelmed with all these tasks"
}).json()

print(f"Detected mood: {mood['detected_mood']}")
# Output: "anxious"

print(f"Recommendation: {mood['recommendation']}")
# Output: "Take a deep breath. Let's prioritize your tasks..."
```

### Example 4: Voice Profile Training

```python
import requests

base_url = "http://localhost:8001/api/v1"

# Create profile
profile = requests.post(f"{base_url}/learning/voice-profile", json={
    "user_id": "john_doe",
    "profile_name": "John's Voice",
    "description": "Primary voice profile"
}).json()

profile_id = profile['profile_id']

# Train with samples
requests.post(f"{base_url}/learning/voice-profile/train", json={
    "profile_id": profile_id,
    "audio_samples": [
        "/recordings/john_sample1.wav",
        "/recordings/john_sample2.wav",
        "/recordings/john_sample3.wav"
    ]
})

# Later, recognize user
recognition = requests.post(f"{base_url}/learning/voice-profile/recognize", json={
    "audio_file": "/recordings/test.wav"
}).json()

print(f"Recognized: {recognition['recognized_user_id']}")
print(f"Confidence: {recognition['confidence']}")
```

### Example 5: Morning Routine Automation

```python
import requests

base_url = "http://localhost:8001/api/v1"

# Get morning routine suggestion
suggestion = requests.get(
    f"{base_url}/learning/suggestions/john_doe/morning-routine"
).json()

if not suggestion['has_routine']:
    # Create suggested routine
    routine = requests.post(f"{base_url}/learning/routines", json={
        "user_id": "john_doe",
        "routine_name": suggestion['suggested_routine']['name'],
        "routine_items": suggestion['suggested_routine']['items'],
        "preferred_time": "07:00",
        "days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    }).json()

    print(f"Created routine: {routine['routine_name']}")
```

---

## Configuration

### Environment Variables

```env
# Enable/disable learning
LEARNING_ENABLED=True

# Pattern detection thresholds
LEARNING_MIN_PATTERN_OCCURRENCES=3
LEARNING_CONFIDENCE_THRESHOLD=0.6
LEARNING_HABIT_THRESHOLD=0.7

# Auto-learning
LEARNING_AUTO_LEARN=True

# Context management
LEARNING_CONTEXT_WINDOW=10
LEARNING_CONTEXT_TIMEOUT_MINUTES=30

# Predictions
LEARNING_PREDICTION_LIMIT=5

# Voice recognition
LEARNING_VOICE_RECOGNITION_THRESHOLD=0.75
```

---

## Best Practices

1. **Regular Usage**
   - Use the assistant regularly for best learning
   - Provide feedback on predictions
   - Update profile as preferences change

2. **Context Management**
   - Keep conversations focused for better context
   - Use session IDs for multi-turn conversations
   - Review and clear old contexts periodically

3. **Mood Detection**
   - Combine text and voice for accuracy
   - Track mood trends over time
   - Adjust responses based on detected mood

4. **Voice Profiles**
   - Train with diverse voice samples
   - Update profiles periodically
   - Provide feedback on recognition accuracy

5. **Privacy**
   - Be aware learning stores interaction history
   - Clear old data periodically
   - Review privacy settings

---

## Troubleshooting

### Learning Not Working

**Check configuration:**
```bash
curl http://localhost:8001/api/v1/learning/health
```

**Verify auto-learning:**
```env
LEARNING_AUTO_LEARN=True
```

### Low Prediction Accuracy

1. **Need more data** - Use assistant more frequently
2. **Provide feedback** - Accept/reject predictions
3. **Check patterns** - Review habit insights
4. **Adjust thresholds** - Lower confidence threshold

### Context Not Remembered

1. **Check timeout** - Increase context timeout
2. **Use session IDs** - Group related conversations
3. **Save context explicitly** - Use context save API

---

## Support

### Resources

- [API Documentation](http://localhost:8001/docs)
- [Main README](../README.md)
- [Voice Setup Guide](../voice_handler/VOICE_SETUP.md)
- [WhatsApp Setup Guide](../whatsapp_handler/WHATSAPP_SETUP.md)

### Getting Help

1. Check API documentation
2. Review logs for errors
3. Test with simple examples first
4. Verify configuration settings

---

Happy learning! 🧠🤖
