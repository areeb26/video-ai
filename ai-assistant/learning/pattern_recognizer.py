"""
Pattern Recognition Module
Detects patterns in user behavior and interactions
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import re
from sqlalchemy.orm import Session


class PatternRecognizer:
    """Recognizes patterns in user behavior"""

    def __init__(self, db: Session):
        self.db = db
        self.min_occurrences = 3  # Minimum occurrences to consider a pattern
        self.confidence_threshold = 0.6

    def analyze_task_patterns(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Analyze patterns in task creation"""
        from ..models.task import Task

        cutoff_date = datetime.now() - timedelta(days=days)
        tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            Task.created_at >= cutoff_date
        ).all()

        patterns = []

        # Time-based patterns
        time_patterns = self._analyze_time_patterns(tasks)
        patterns.extend(time_patterns)

        # Title-based patterns (recurring task types)
        title_patterns = self._analyze_title_patterns(tasks)
        patterns.extend(title_patterns)

        # Priority patterns
        priority_patterns = self._analyze_priority_patterns(tasks)
        patterns.extend(priority_patterns)

        return patterns

    def _analyze_time_patterns(self, tasks: List[Any]) -> List[Dict[str, Any]]:
        """Analyze when user creates tasks"""
        patterns = []

        # Group by time of day
        time_groups = defaultdict(list)
        for task in tasks:
            hour = task.created_at.hour
            time_of_day = self._get_time_of_day(hour)
            time_groups[time_of_day].append(task)

        for time_of_day, time_tasks in time_groups.items():
            if len(time_tasks) >= self.min_occurrences:
                # Extract common task types
                titles = [t.title.lower() for t in time_tasks]
                common_words = self._extract_common_words(titles)

                patterns.append({
                    "type": "time_based",
                    "time_of_day": time_of_day,
                    "frequency": len(time_tasks),
                    "confidence": min(len(time_tasks) / len(tasks), 1.0),
                    "common_keywords": common_words[:5],
                    "description": f"User often creates tasks in the {time_of_day}"
                })

        # Group by day of week
        day_groups = defaultdict(list)
        for task in tasks:
            day = task.created_at.strftime("%A").lower()
            day_groups[day].append(task)

        for day, day_tasks in day_groups.items():
            if len(day_tasks) >= self.min_occurrences:
                patterns.append({
                    "type": "day_based",
                    "day_of_week": day,
                    "frequency": len(day_tasks),
                    "confidence": min(len(day_tasks) / (len(tasks) / 7), 1.0),
                    "description": f"User creates more tasks on {day}"
                })

        return patterns

    def _analyze_title_patterns(self, tasks: List[Any]) -> List[Dict[str, Any]]:
        """Analyze recurring task types"""
        patterns = []

        # Extract keywords from all task titles
        all_keywords = []
        for task in tasks:
            keywords = self._extract_keywords(task.title)
            all_keywords.extend(keywords)

        # Count keyword frequency
        keyword_counts = Counter(all_keywords)

        # Find recurring keywords
        for keyword, count in keyword_counts.most_common(10):
            if count >= self.min_occurrences:
                # Find tasks with this keyword
                related_tasks = [t for t in tasks if keyword in t.title.lower()]

                patterns.append({
                    "type": "recurring_task",
                    "keyword": keyword,
                    "frequency": count,
                    "confidence": min(count / len(tasks), 1.0),
                    "sample_titles": [t.title for t in related_tasks[:3]],
                    "description": f"User frequently creates tasks related to '{keyword}'"
                })

        return patterns

    def _analyze_priority_patterns(self, tasks: List[Any]) -> List[Dict[str, Any]]:
        """Analyze priority preferences"""
        patterns = []

        priority_counts = Counter([t.priority for t in tasks])

        for priority, count in priority_counts.items():
            if count >= self.min_occurrences:
                patterns.append({
                    "type": "priority_preference",
                    "priority": priority,
                    "frequency": count,
                    "confidence": count / len(tasks),
                    "description": f"User prefers '{priority}' priority"
                })

        return patterns

    def analyze_command_patterns(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Analyze patterns in command execution"""
        from ..models.command_history import CommandHistory

        cutoff_date = datetime.now() - timedelta(days=days)
        commands = self.db.query(CommandHistory).filter(
            CommandHistory.user_id == user_id,
            CommandHistory.executed_at >= cutoff_date
        ).all()

        patterns = []

        # Command type patterns
        command_counts = Counter([c.command_type for c in commands])

        for cmd_type, count in command_counts.most_common():
            if count >= self.min_occurrences:
                patterns.append({
                    "type": "command_usage",
                    "command_type": cmd_type,
                    "frequency": count,
                    "confidence": count / len(commands) if commands else 0,
                    "description": f"User frequently uses '{cmd_type}' commands"
                })

        # Time-based command patterns
        time_groups = defaultdict(list)
        for cmd in commands:
            hour = cmd.executed_at.hour
            time_of_day = self._get_time_of_day(hour)
            time_groups[time_of_day].append(cmd)

        for time_of_day, time_cmds in time_groups.items():
            if len(time_cmds) >= self.min_occurrences:
                common_types = Counter([c.command_type for c in time_cmds]).most_common(3)

                patterns.append({
                    "type": "time_command",
                    "time_of_day": time_of_day,
                    "frequency": len(time_cmds),
                    "common_commands": [{"type": t, "count": c} for t, c in common_types],
                    "confidence": len(time_cmds) / len(commands) if commands else 0,
                    "description": f"User executes commands in the {time_of_day}"
                })

        return patterns

    def analyze_conversation_patterns(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Analyze conversation patterns"""
        from ..models.user_profile import ConversationContext

        cutoff_date = datetime.now() - timedelta(days=days)
        contexts = self.db.query(ConversationContext).filter(
            ConversationContext.user_id == user_id,
            ConversationContext.timestamp >= cutoff_date
        ).all()

        patterns = []

        if not contexts:
            return patterns

        # Language preferences
        language_counts = Counter([c.language for c in contexts])
        for lang, count in language_counts.items():
            patterns.append({
                "type": "language_preference",
                "language": lang,
                "frequency": count,
                "confidence": count / len(contexts),
                "description": f"User prefers {lang} language"
            })

        # Channel preferences
        channel_counts = Counter([c.channel for c in contexts])
        for channel, count in channel_counts.items():
            if count >= self.min_occurrences:
                patterns.append({
                    "type": "channel_preference",
                    "channel": channel,
                    "frequency": count,
                    "confidence": count / len(contexts),
                    "description": f"User frequently uses {channel} channel"
                })

        # Intent patterns
        intent_counts = Counter([c.intent for c in contexts if c.intent])
        for intent, count in intent_counts.most_common(5):
            if count >= self.min_occurrences:
                patterns.append({
                    "type": "intent_pattern",
                    "intent": intent,
                    "frequency": count,
                    "confidence": count / len(contexts),
                    "description": f"User frequently requests '{intent}'"
                })

        return patterns

    def detect_new_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """Detect all patterns for a user"""
        all_patterns = []

        # Task patterns
        all_patterns.extend(self.analyze_task_patterns(user_id))

        # Command patterns
        all_patterns.extend(self.analyze_command_patterns(user_id))

        # Conversation patterns
        all_patterns.extend(self.analyze_conversation_patterns(user_id))

        # Filter by confidence
        filtered_patterns = [
            p for p in all_patterns
            if p.get('confidence', 0) >= self.confidence_threshold
        ]

        # Sort by confidence
        filtered_patterns.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        return filtered_patterns

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
        # Remove common stop words
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can'
        }

        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter stop words and short words
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        return keywords

    def _extract_common_words(self, texts: List[str]) -> List[str]:
        """Extract most common words from texts"""
        all_keywords = []
        for text in texts:
            all_keywords.extend(self._extract_keywords(text))

        word_counts = Counter(all_keywords)
        return [word for word, count in word_counts.most_common(10)]

    def calculate_pattern_similarity(self, pattern1: Dict[str, Any], pattern2: Dict[str, Any]) -> float:
        """Calculate similarity between two patterns"""
        if pattern1['type'] != pattern2['type']:
            return 0.0

        similarity = 0.0

        # Compare based on pattern type
        if pattern1['type'] == 'time_based':
            if pattern1.get('time_of_day') == pattern2.get('time_of_day'):
                similarity += 0.5

            # Compare keywords
            keywords1 = set(pattern1.get('common_keywords', []))
            keywords2 = set(pattern2.get('common_keywords', []))
            if keywords1 and keywords2:
                overlap = len(keywords1 & keywords2) / max(len(keywords1), len(keywords2))
                similarity += 0.5 * overlap

        elif pattern1['type'] == 'recurring_task':
            if pattern1.get('keyword') == pattern2.get('keyword'):
                similarity = 1.0

        return min(similarity, 1.0)
