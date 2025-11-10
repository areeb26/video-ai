"""
Task Prediction Module
Predicts tasks based on user habits and patterns
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import random


class TaskPredictor:
    """Predicts tasks user might want to create"""

    def __init__(self, db: Session):
        self.db = db
        self.min_confidence = 0.6

    def predict_tasks(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Predict tasks based on user habits"""
        from ..models.user_profile import UserHabit, TaskPrediction

        predictions = []

        # Get current context
        now = datetime.now()
        current_hour = now.hour
        current_time_of_day = self._get_time_of_day(current_hour)
        current_day = now.strftime("%A").lower()

        # Get relevant habits
        habits = self.db.query(UserHabit).filter(
            UserHabit.user_id == user_id,
            UserHabit.confidence >= self.min_confidence
        ).order_by(UserHabit.confidence.desc()).all()

        # Predict based on time patterns
        time_based_predictions = self._predict_from_time_patterns(
            user_id, habits, current_time_of_day, current_day
        )
        predictions.extend(time_based_predictions)

        # Predict based on recurring tasks
        recurring_predictions = self._predict_from_recurring_tasks(user_id, habits)
        predictions.extend(recurring_predictions)

        # Predict based on task history
        history_predictions = self._predict_from_history(user_id, current_time_of_day)
        predictions.extend(history_predictions)

        # Remove duplicates and sort by confidence
        unique_predictions = self._deduplicate_predictions(predictions)
        unique_predictions.sort(key=lambda x: x['confidence'], reverse=True)

        # Store predictions in database
        for pred in unique_predictions[:limit]:
            # Check if already exists and not dismissed
            existing = self.db.query(TaskPrediction).filter(
                TaskPrediction.user_id == user_id,
                TaskPrediction.predicted_task == pred['task'],
                TaskPrediction.dismissed_by_user == False,
                TaskPrediction.created_at >= datetime.now() - timedelta(hours=24)
            ).first()

            if not existing:
                prediction = TaskPrediction(
                    user_id=user_id,
                    predicted_task=pred['task'],
                    prediction_reason=pred['reason'],
                    confidence_score=pred['confidence'],
                    time_of_day=pred.get('time_of_day'),
                    day_of_week=pred.get('day_of_week'),
                    based_on_patterns=pred.get('patterns', [])
                )
                self.db.add(prediction)

        self.db.commit()

        return unique_predictions[:limit]

    def _predict_from_time_patterns(
        self,
        user_id: str,
        habits: List[Any],
        time_of_day: str,
        day_of_week: str
    ) -> List[Dict[str, Any]]:
        """Predict tasks based on time patterns"""
        predictions = []

        # Filter habits by current time
        time_habits = [
            h for h in habits
            if h.time_of_day == time_of_day and h.habit_type == 'recurring_task'
        ]

        for habit in time_habits:
            keyword = habit.pattern_data.get('keyword', '')
            if keyword:
                task_title = self._generate_task_from_keyword(keyword)
                predictions.append({
                    'task': task_title,
                    'reason': f"You usually create tasks like this in the {time_of_day}",
                    'confidence': habit.confidence * 0.9,  # Slight discount for prediction
                    'time_of_day': time_of_day,
                    'day_of_week': day_of_week,
                    'patterns': [habit.pattern_data]
                })

        return predictions

    def _predict_from_recurring_tasks(self, user_id: str, habits: List[Any]) -> List[Dict[str, Any]]:
        """Predict tasks based on recurring task habits"""
        from ..models.task import Task

        predictions = []

        recurring_habits = [h for h in habits if h.habit_type == 'recurring_task']

        for habit in recurring_habits:
            keyword = habit.pattern_data.get('keyword', '')

            # Check when this task was last created
            last_task = self.db.query(Task).filter(
                Task.user_id == user_id,
                Task.title.ilike(f'%{keyword}%')
            ).order_by(Task.created_at.desc()).first()

            # If not created recently, predict it
            if not last_task or (datetime.now() - last_task.created_at).days >= 7:
                task_title = habit.pattern_data.get('title', self._generate_task_from_keyword(keyword))
                predictions.append({
                    'task': task_title,
                    'reason': f"You haven't created a '{keyword}' task recently",
                    'confidence': habit.confidence * 0.85,
                    'patterns': [habit.pattern_data]
                })

        return predictions

    def _predict_from_history(self, user_id: str, time_of_day: str) -> List[Dict[str, Any]]:
        """Predict based on historical task patterns"""
        from ..models.task import Task

        predictions = []

        # Get tasks from same time last week
        one_week_ago = datetime.now() - timedelta(days=7)
        week_start = one_week_ago.replace(hour=0, minute=0, second=0)
        week_end = one_week_ago.replace(hour=23, minute=59, second=59)

        similar_time_tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            Task.created_at >= week_start,
            Task.created_at <= week_end
        ).all()

        for task in similar_time_tasks:
            # Check if similar task exists this week
            this_week_start = datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=datetime.now().weekday())
            similar_this_week = self.db.query(Task).filter(
                Task.user_id == user_id,
                Task.title.ilike(f'%{task.title[:20]}%'),
                Task.created_at >= this_week_start
            ).first()

            if not similar_this_week:
                predictions.append({
                    'task': task.title,
                    'reason': "You created a similar task last week",
                    'confidence': 0.7,
                    'time_of_day': time_of_day,
                    'patterns': [{'type': 'weekly_pattern', 'previous_task': task.title}]
                })

        return predictions

    def _deduplicate_predictions(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate predictions"""
        seen = set()
        unique = []

        for pred in predictions:
            task_lower = pred['task'].lower().strip()
            if task_lower not in seen:
                seen.add(task_lower)
                unique.append(pred)

        return unique

    def _generate_task_from_keyword(self, keyword: str) -> str:
        """Generate a task title from keyword"""
        templates = [
            f"Work on {keyword}",
            f"Complete {keyword}",
            f"Review {keyword}",
            f"Update {keyword}",
            f"Check {keyword}"
        ]
        return random.choice(templates)

    def get_predictions_for_user(self, user_id: str, include_dismissed: bool = False) -> List[Dict[str, Any]]:
        """Get stored predictions for user"""
        from ..models.user_profile import TaskPrediction

        query = self.db.query(TaskPrediction).filter(
            TaskPrediction.user_id == user_id,
            TaskPrediction.shown_to_user == False
        )

        if not include_dismissed:
            query = query.filter(TaskPrediction.dismissed_by_user == False)

        predictions = query.order_by(TaskPrediction.confidence_score.desc()).all()

        return [
            {
                'id': p.id,
                'task': p.predicted_task,
                'reason': p.prediction_reason,
                'confidence': p.confidence_score,
                'time_of_day': p.time_of_day,
                'day_of_week': p.day_of_week,
                'patterns': p.based_on_patterns,
                'created_at': p.created_at
            }
            for p in predictions
        ]

    def accept_prediction(self, user_id: str, prediction_id: int) -> bool:
        """Mark prediction as accepted"""
        from ..models.user_profile import TaskPrediction

        prediction = self.db.query(TaskPrediction).filter(
            TaskPrediction.id == prediction_id,
            TaskPrediction.user_id == user_id
        ).first()

        if prediction:
            prediction.accepted_by_user = True
            prediction.accepted_at = datetime.now()
            prediction.shown_to_user = True
            self.db.commit()
            return True

        return False

    def dismiss_prediction(self, user_id: str, prediction_id: int) -> bool:
        """Mark prediction as dismissed"""
        from ..models.user_profile import TaskPrediction

        prediction = self.db.query(TaskPrediction).filter(
            TaskPrediction.id == prediction_id,
            TaskPrediction.user_id == user_id
        ).first()

        if prediction:
            prediction.dismissed_by_user = True
            prediction.shown_to_user = True
            self.db.commit()
            return True

        return False

    def get_prediction_accuracy(self, user_id: str) -> Dict[str, Any]:
        """Calculate prediction accuracy for user"""
        from ..models.user_profile import TaskPrediction

        total = self.db.query(TaskPrediction).filter(
            TaskPrediction.user_id == user_id,
            TaskPrediction.shown_to_user == True
        ).count()

        accepted = self.db.query(TaskPrediction).filter(
            TaskPrediction.user_id == user_id,
            TaskPrediction.accepted_by_user == True
        ).count()

        dismissed = self.db.query(TaskPrediction).filter(
            TaskPrediction.user_id == user_id,
            TaskPrediction.dismissed_by_user == True
        ).count()

        accuracy = accepted / total if total > 0 else 0.0

        return {
            'total_predictions': total,
            'accepted': accepted,
            'dismissed': dismissed,
            'accuracy': accuracy,
            'acceptance_rate': accuracy
        }

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
