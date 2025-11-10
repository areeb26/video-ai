"""
Personalized Suggestion Engine
Generates personalized suggestions based on user habits and context
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .habit_learner import HabitLearner
from .task_predictor import TaskPredictor
from .context_manager import ContextManager


class SuggestionEngine:
    """Generates personalized suggestions for users"""

    def __init__(self, db: Session):
        self.db = db
        self.habit_learner = HabitLearner(db)
        self.task_predictor = TaskPredictor(db)
        self.context_manager = ContextManager(db)

    def get_personalized_suggestions(
        self,
        user_id: str,
        context: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """Get all types of personalized suggestions"""

        suggestions = {
            'tasks': [],
            'routines': [],
            'commands': [],
            'responses': [],
            'based_on': []
        }

        # Get task suggestions
        task_suggestions = self.get_task_suggestions(user_id, limit=limit)
        suggestions['tasks'] = task_suggestions['suggestions']
        suggestions['based_on'].extend(task_suggestions['based_on'])

        # Get routine suggestions
        routine_suggestions = self.get_routine_suggestions(user_id)
        suggestions['routines'] = routine_suggestions['suggestions']
        suggestions['based_on'].extend(routine_suggestions['based_on'])

        # Get command suggestions
        command_suggestions = self.get_command_suggestions(user_id, context)
        suggestions['commands'] = command_suggestions['suggestions']
        suggestions['based_on'].extend(command_suggestions['based_on'])

        # Get response suggestions based on context
        if context:
            response_suggestions = self.get_response_suggestions(user_id, context)
            suggestions['responses'] = response_suggestions['suggestions']
            suggestions['based_on'].extend(response_suggestions['based_on'])

        return suggestions

    def get_task_suggestions(self, user_id: str, limit: int = 5) -> Dict[str, Any]:
        """Get task suggestions"""
        predictions = self.task_predictor.predict_tasks(user_id, limit=limit)

        suggestions = [
            {
                'type': 'task',
                'content': pred['task'],
                'reason': pred['reason'],
                'confidence': pred['confidence'],
                'action': 'create_task',
                'action_data': {'title': pred['task']}
            }
            for pred in predictions
        ]

        based_on = ['task_history', 'recurring_patterns', 'time_patterns']

        return {
            'suggestions': suggestions,
            'based_on': based_on
        }

    def get_routine_suggestions(self, user_id: str) -> Dict[str, Any]:
        """Get morning routine suggestions"""
        from ..models.user_profile import MorningRoutine

        # Check if user has routines
        existing_routines = self.db.query(MorningRoutine).filter(
            MorningRoutine.user_id == user_id,
            MorningRoutine.is_active == True
        ).all()

        suggestions = []

        if not existing_routines:
            # Suggest creating a morning routine based on habits
            morning_habits = self.habit_learner.get_user_habits(user_id, habit_type='time_based')

            morning_specific = [h for h in morning_habits if h.get('time_of_day') == 'morning']

            if morning_specific:
                suggested_items = [
                    {
                        'action': h['pattern_data'].get('keyword', 'task'),
                        'time': '07:00'
                    }
                    for h in morning_specific[:5]
                ]

                suggestions.append({
                    'type': 'routine',
                    'content': 'Create a morning routine',
                    'reason': 'Based on your morning habits',
                    'confidence': 0.75,
                    'action': 'create_routine',
                    'action_data': {
                        'routine_name': 'Morning Routine',
                        'routine_items': suggested_items,
                        'preferred_time': '07:00'
                    }
                })
        else:
            # Suggest optimizing existing routines
            for routine in existing_routines:
                if routine.times_executed > 10 and routine.times_modified == 0:
                    suggestions.append({
                        'type': 'routine',
                        'content': f'Review your {routine.routine_name}',
                        'reason': 'You might want to optimize it based on recent habits',
                        'confidence': 0.6,
                        'action': 'review_routine',
                        'action_data': {'routine_id': routine.id}
                    })

        based_on = ['morning_habits', 'time_patterns']

        return {
            'suggestions': suggestions,
            'based_on': based_on
        }

    def get_command_suggestions(
        self,
        user_id: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get command suggestions"""
        habits = self.habit_learner.get_user_habits(user_id, habit_type='command_usage')

        now = datetime.now()
        current_time_of_day = self._get_time_of_day(now.hour)

        # Filter habits by current time
        relevant_habits = [
            h for h in habits
            if h.get('time_of_day') == current_time_of_day
        ]

        suggestions = []

        for habit in relevant_habits[:5]:
            command_type = habit['pattern_data'].get('command_type', 'unknown')

            suggestions.append({
                'type': 'command',
                'content': f"Run {command_type} command",
                'reason': f"You usually use this command in the {current_time_of_day}",
                'confidence': habit['confidence'],
                'action': 'execute_command',
                'action_data': {'command_type': command_type}
            })

        based_on = ['command_history', 'time_patterns']

        return {
            'suggestions': suggestions,
            'based_on': based_on
        }

    def get_response_suggestions(
        self,
        user_id: str,
        current_message: str
    ) -> Dict[str, Any]:
        """Get response suggestions based on context"""
        # Get recent context
        recent_contexts = self.context_manager.get_recent_context(user_id, limit=5)

        suggestions = []

        if recent_contexts:
            last_context = recent_contexts[-1]
            last_intent = last_context.get('intent')

            # Suggest follow-up actions
            if last_intent == 'create_task':
                suggestions.extend([
                    {
                        'type': 'response',
                        'content': 'Set a reminder',
                        'reason': 'Common follow-up to creating a task',
                        'confidence': 0.7,
                        'action': 'set_reminder'
                    },
                    {
                        'type': 'response',
                        'content': 'Add more details',
                        'reason': 'You might want to specify more',
                        'confidence': 0.6,
                        'action': 'update_task'
                    }
                ])

            elif last_intent == 'list_tasks':
                suggestions.extend([
                    {
                        'type': 'response',
                        'content': 'Mark a task as done',
                        'reason': 'Common next action after viewing tasks',
                        'confidence': 0.75,
                        'action': 'complete_task'
                    },
                    {
                        'type': 'response',
                        'content': 'Filter by priority',
                        'reason': 'Focus on important tasks',
                        'confidence': 0.65,
                        'action': 'filter_tasks'
                    }
                ])

        # Check for follow-up words
        follow_up_words = ['yes', 'no', 'okay', 'sure', 'done']
        if any(word in current_message.lower() for word in follow_up_words):
            if recent_contexts:
                suggestions.append({
                    'type': 'response',
                    'content': 'Referring to previous conversation',
                    'reason': 'Detected follow-up response',
                    'confidence': 0.8,
                    'action': 'context_aware_response'
                })

        based_on = ['conversation_context', 'follow_up_patterns']

        return {
            'suggestions': suggestions,
            'based_on': based_on
        }

    def get_morning_routine_suggestion(self, user_id: str) -> Dict[str, Any]:
        """Get personalized morning routine suggestion"""
        from ..models.user_profile import MorningRoutine

        # Check if user already has a morning routine
        existing = self.db.query(MorningRoutine).filter(
            MorningRoutine.user_id == user_id,
            MorningRoutine.is_active == True
        ).first()

        if existing:
            return {
                'has_routine': True,
                'routine': {
                    'id': existing.id,
                    'name': existing.routine_name,
                    'items': existing.routine_items,
                    'time': existing.preferred_time
                },
                'suggestion': 'Continue with your existing routine'
            }

        # Create suggestion based on habits
        morning_habits = self.habit_learner.get_user_habits(user_id)
        morning_specific = [h for h in morning_habits if h.get('time_of_day') == 'morning']

        if morning_specific:
            routine_items = []

            for habit in morning_specific[:5]:
                keyword = habit['pattern_data'].get('keyword', '')
                if keyword:
                    routine_items.append({
                        'task': f"Work on {keyword}",
                        'time': '07:00',
                        'duration': 30
                    })

            return {
                'has_routine': False,
                'suggestion': 'Create a morning routine',
                'suggested_routine': {
                    'name': 'Personalized Morning Routine',
                    'items': routine_items,
                    'confidence': 0.75
                }
            }

        # Default suggestion if no habits
        return {
            'has_routine': False,
            'suggestion': 'Start building morning habits',
            'suggested_routine': {
                'name': 'Basic Morning Routine',
                'items': [
                    {'task': 'Review today\'s tasks', 'time': '07:00', 'duration': 15},
                    {'task': 'Plan priorities', 'time': '07:15', 'duration': 15}
                ],
                'confidence': 0.5
            }
        }

    def get_auto_suggestions_based_on_time(self, user_id: str) -> List[Dict[str, Any]]:
        """Get auto-suggestions based on current time"""
        now = datetime.now()
        current_hour = now.hour
        current_day = now.strftime("%A").lower()
        time_of_day = self._get_time_of_day(current_hour)

        suggestions = []

        # Morning suggestions (5 AM - 9 AM)
        if 5 <= current_hour < 9:
            routine_suggestion = self.get_morning_routine_suggestion(user_id)
            if not routine_suggestion['has_routine']:
                suggestions.append({
                    'content': 'Start your morning routine',
                    'reason': 'It\'s morning time',
                    'confidence': 0.8
                })

        # End of workday suggestions (5 PM - 6 PM)
        if 17 <= current_hour < 18:
            suggestions.append({
                'content': 'Review today\'s completed tasks',
                'reason': 'End of workday wrap-up',
                'confidence': 0.75
            })
            suggestions.append({
                'content': 'Plan tomorrow\'s tasks',
                'reason': 'Prepare for tomorrow',
                'confidence': 0.7
            })

        # Evening wind-down (9 PM - 11 PM)
        if 21 <= current_hour < 23:
            suggestions.append({
                'content': 'Check tomorrow\'s schedule',
                'reason': 'Evening preparation',
                'confidence': 0.65
            })

        # Monday morning
        if current_day == 'monday' and 7 <= current_hour < 10:
            suggestions.append({
                'content': 'Plan your week',
                'reason': 'Start of the week',
                'confidence': 0.8
            })

        # Friday afternoon
        if current_day == 'friday' and 14 <= current_hour < 17:
            suggestions.append({
                'content': 'Wrap up weekly tasks',
                'reason': 'End of the week',
                'confidence': 0.75
            })

        return suggestions

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

    def get_contextual_suggestions(
        self,
        user_id: str,
        current_intent: str,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Get suggestions based on current intent"""
        suggestions = []

        intent_suggestions = {
            'create_task': [
                ('Set reminder', 'set_reminder', 0.7),
                ('Add due date', 'set_due_date', 0.65),
                ('Set priority', 'set_priority', 0.6)
            ],
            'list_tasks': [
                ('Filter by priority', 'filter_priority', 0.7),
                ('Show completed', 'show_completed', 0.6),
                ('Sort by date', 'sort_by_date', 0.65)
            ],
            'send_whatsapp': [
                ('Schedule message', 'schedule_message', 0.7),
                ('Send to group', 'send_to_group', 0.6),
                ('Send file', 'send_file', 0.65)
            ]
        }

        if current_intent in intent_suggestions:
            for content, action, confidence in intent_suggestions[current_intent]:
                suggestions.append({
                    'content': content,
                    'action': action,
                    'confidence': confidence
                })

        return suggestions
