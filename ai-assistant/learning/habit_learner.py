"""
Habit Learning Module
Learns and stores user habits based on patterns
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .pattern_recognizer import PatternRecognizer


class HabitLearner:
    """Learns user habits from patterns"""

    def __init__(self, db: Session):
        self.db = db
        self.pattern_recognizer = PatternRecognizer(db)
        self.habit_threshold = 0.7  # Confidence threshold to save as habit

    def learn_habits(self, user_id: str) -> List[Dict[str, Any]]:
        """Learn habits from user patterns"""
        from ..models.user_profile import UserHabit

        # Detect patterns
        patterns = self.pattern_recognizer.detect_new_patterns(user_id)

        new_habits = []

        for pattern in patterns:
            if pattern['confidence'] >= self.habit_threshold:
                # Check if habit already exists
                existing_habit = self.db.query(UserHabit).filter(
                    UserHabit.user_id == user_id,
                    UserHabit.habit_type == pattern['type'],
                    UserHabit.pattern_data['keyword'].astext == pattern.get('keyword', '')
                ).first() if pattern.get('keyword') else None

                if existing_habit:
                    # Update existing habit
                    existing_habit.frequency += 1
                    existing_habit.confidence = pattern['confidence']
                    existing_habit.last_occurrence = datetime.now()
                    existing_habit.pattern_data = pattern
                    self.db.commit()
                else:
                    # Create new habit
                    habit = UserHabit(
                        user_id=user_id,
                        habit_type=pattern['type'],
                        pattern_data=pattern,
                        frequency=pattern['frequency'],
                        confidence=pattern['confidence'],
                        time_of_day=pattern.get('time_of_day'),
                        day_of_week=pattern.get('day_of_week'),
                        last_occurrence=datetime.now()
                    )
                    self.db.add(habit)
                    self.db.commit()
                    new_habits.append(pattern)

        return new_habits

    def get_user_habits(self, user_id: str, habit_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get learned habits for a user"""
        from ..models.user_profile import UserHabit

        query = self.db.query(UserHabit).filter(UserHabit.user_id == user_id)

        if habit_type:
            query = query.filter(UserHabit.habit_type == habit_type)

        habits = query.order_by(UserHabit.confidence.desc()).all()

        return [
            {
                'id': h.id,
                'habit_type': h.habit_type,
                'pattern_data': h.pattern_data,
                'frequency': h.frequency,
                'confidence': h.confidence,
                'time_of_day': h.time_of_day,
                'day_of_week': h.day_of_week,
                'last_occurrence': h.last_occurrence
            }
            for h in habits
        ]

    def update_habit_from_action(self, user_id: str, action_type: str, action_data: Dict[str, Any]):
        """Update habits when user performs an action"""
        from ..models.user_profile import UserHabit

        # Determine habit type from action
        if action_type == 'task_created':
            self._update_task_habit(user_id, action_data)
        elif action_type == 'command_executed':
            self._update_command_habit(user_id, action_data)
        elif action_type == 'conversation':
            self._update_conversation_habit(user_id, action_data)

        # Update user profile statistics
        from ..models.user_profile import UserProfile
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

        if profile:
            profile.last_interaction = datetime.now()
            if action_type == 'task_created':
                profile.total_tasks_created += 1
            elif action_type == 'command_executed':
                profile.total_commands_executed += 1
            elif action_type == 'conversation' and action_data.get('channel') == 'voice':
                profile.total_voice_interactions += 1

            self.db.commit()

    def _update_task_habit(self, user_id: str, task_data: Dict[str, Any]):
        """Update habits when task is created"""
        from ..models.user_profile import UserHabit

        now = datetime.now()
        time_of_day = self._get_time_of_day(now.hour)
        day_of_week = now.strftime("%A").lower()

        # Extract keywords from task title
        keywords = self._extract_keywords(task_data.get('title', ''))

        for keyword in keywords[:3]:  # Top 3 keywords
            # Find or create habit
            habit = self.db.query(UserHabit).filter(
                UserHabit.user_id == user_id,
                UserHabit.habit_type == 'recurring_task',
                UserHabit.pattern_data['keyword'].astext == keyword
            ).first()

            if habit:
                habit.frequency += 1
                habit.last_occurrence = now
                habit.confidence = min(habit.confidence + 0.05, 1.0)
            else:
                habit = UserHabit(
                    user_id=user_id,
                    habit_type='recurring_task',
                    pattern_data={'keyword': keyword, 'title': task_data.get('title')},
                    frequency=1,
                    confidence=0.5,
                    time_of_day=time_of_day,
                    day_of_week=day_of_week,
                    last_occurrence=now
                )
                self.db.add(habit)

        self.db.commit()

    def _update_command_habit(self, user_id: str, command_data: Dict[str, Any]):
        """Update habits when command is executed"""
        from ..models.user_profile import UserHabit

        now = datetime.now()
        time_of_day = self._get_time_of_day(now.hour)

        command_type = command_data.get('command_type', 'unknown')

        # Find or create habit
        habit = self.db.query(UserHabit).filter(
            UserHabit.user_id == user_id,
            UserHabit.habit_type == 'command_usage',
            UserHabit.pattern_data['command_type'].astext == command_type
        ).first()

        if habit:
            habit.frequency += 1
            habit.last_occurrence = now
            habit.confidence = min(habit.confidence + 0.05, 1.0)
        else:
            habit = UserHabit(
                user_id=user_id,
                habit_type='command_usage',
                pattern_data={'command_type': command_type},
                frequency=1,
                confidence=0.5,
                time_of_day=time_of_day,
                last_occurrence=now
            )
            self.db.add(habit)

        self.db.commit()

    def _update_conversation_habit(self, user_id: str, conversation_data: Dict[str, Any]):
        """Update habits from conversation"""
        from ..models.user_profile import UserHabit

        language = conversation_data.get('language', 'en')
        channel = conversation_data.get('channel', 'text')

        # Language habit
        habit = self.db.query(UserHabit).filter(
            UserHabit.user_id == user_id,
            UserHabit.habit_type == 'language_preference',
            UserHabit.pattern_data['language'].astext == language
        ).first()

        if habit:
            habit.frequency += 1
            habit.confidence = min(habit.confidence + 0.05, 1.0)
        else:
            habit = UserHabit(
                user_id=user_id,
                habit_type='language_preference',
                pattern_data={'language': language},
                frequency=1,
                confidence=0.5
            )
            self.db.add(habit)

        # Channel habit
        habit = self.db.query(UserHabit).filter(
            UserHabit.user_id == user_id,
            UserHabit.habit_type == 'channel_preference',
            UserHabit.pattern_data['channel'].astext == channel
        ).first()

        if habit:
            habit.frequency += 1
            habit.confidence = min(habit.confidence + 0.05, 1.0)
        else:
            habit = UserHabit(
                user_id=user_id,
                habit_type='channel_preference',
                pattern_data={'channel': channel},
                frequency=1,
                confidence=0.5
            )
            self.db.add(habit)

        self.db.commit()

    def get_habit_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights from learned habits"""
        habits = self.get_user_habits(user_id)

        insights = {
            'total_habits': len(habits),
            'habit_categories': {},
            'strongest_habits': [],
            'recent_habits': [],
            'time_preferences': {},
            'day_preferences': {}
        }

        # Group by category
        for habit in habits:
            habit_type = habit['habit_type']
            if habit_type not in insights['habit_categories']:
                insights['habit_categories'][habit_type] = 0
            insights['habit_categories'][habit_type] += 1

        # Top 5 strongest habits
        sorted_habits = sorted(habits, key=lambda x: x['confidence'], reverse=True)
        insights['strongest_habits'] = sorted_habits[:5]

        # Recent habits (last 7 days)
        recent_cutoff = datetime.now() - timedelta(days=7)
        insights['recent_habits'] = [
            h for h in habits
            if h.get('last_occurrence') and h['last_occurrence'] >= recent_cutoff
        ]

        # Time preferences
        time_habits = [h for h in habits if h.get('time_of_day')]
        for h in time_habits:
            tod = h['time_of_day']
            if tod not in insights['time_preferences']:
                insights['time_preferences'][tod] = 0
            insights['time_preferences'][tod] += 1

        # Day preferences
        day_habits = [h for h in habits if h.get('day_of_week')]
        for h in day_habits:
            dow = h['day_of_week']
            if dow not in insights['day_preferences']:
                insights['day_preferences'][dow] = 0
            insights['day_preferences'][dow] += 1

        return insights

    def _get_time_of_day(self, hour: int) -> str:
        """Convert hour to time of day category"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        import re
        from collections import Counter

        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be'
        }

        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        return keywords
