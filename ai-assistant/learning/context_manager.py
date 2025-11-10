"""
Context Manager Module
Manages conversation context for context-aware responses
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session


class ContextManager:
    """Manages conversation context and history"""

    def __init__(self, db: Session):
        self.db = db
        self.default_context_window = 10
        self.context_timeout_minutes = 30

    def save_context(
        self,
        user_id: str,
        user_message: str,
        assistant_response: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None,
        language: str = "en",
        channel: str = "text",
        session_id: Optional[str] = None,
        mood_data: Optional[Dict[str, Any]] = None
    ) -> int:
        """Save conversation context"""
        from ..models.user_profile import ConversationContext

        context = ConversationContext(
            user_id=user_id,
            session_id=session_id,
            user_message=user_message,
            assistant_response=assistant_response,
            intent=intent,
            entities=entities or {},
            language=language,
            channel=channel,
            detected_mood=mood_data.get('mood') if mood_data else None,
            mood_confidence=mood_data.get('confidence') if mood_data else None,
            voice_pitch=mood_data.get('pitch') if mood_data else None,
            voice_energy=mood_data.get('energy') if mood_data else None,
            voice_rate=mood_data.get('rate') if mood_data else None
        )

        self.db.add(context)
        self.db.commit()
        self.db.refresh(context)

        return context.id

    def get_recent_context(
        self,
        user_id: str,
        limit: int = None,
        session_id: Optional[str] = None,
        include_expired: bool = False
    ) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        from ..models.user_profile import ConversationContext

        limit = limit or self.default_context_window

        query = self.db.query(ConversationContext).filter(
            ConversationContext.user_id == user_id
        )

        if session_id:
            query = query.filter(ConversationContext.session_id == session_id)

        if not include_expired:
            cutoff = datetime.now() - timedelta(minutes=self.context_timeout_minutes)
            query = query.filter(ConversationContext.timestamp >= cutoff)

        contexts = query.order_by(
            ConversationContext.timestamp.desc()
        ).limit(limit).all()

        # Reverse to get chronological order
        contexts = list(reversed(contexts))

        return [
            {
                'id': c.id,
                'user_message': c.user_message,
                'assistant_response': c.assistant_response,
                'intent': c.intent,
                'entities': c.entities,
                'language': c.language,
                'channel': c.channel,
                'mood': c.detected_mood,
                'timestamp': c.timestamp
            }
            for c in contexts
        ]

    def get_contextual_response(
        self,
        user_id: str,
        current_message: str,
        language: str = "en",
        session_id: Optional[str] = None
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """Get context-aware response suggestions"""
        # Get recent context
        recent_contexts = self.get_recent_context(
            user_id=user_id,
            session_id=session_id,
            limit=5
        )

        # Analyze current message with context
        suggestions = self._generate_suggestions(
            current_message=current_message,
            recent_contexts=recent_contexts,
            language=language
        )

        # Extract relevant previous contexts
        relevant_contexts = self._find_relevant_contexts(
            current_message=current_message,
            contexts=recent_contexts
        )

        # Generate context-aware intent
        intent = self._determine_intent_with_context(
            current_message=current_message,
            recent_contexts=recent_contexts
        )

        return intent, relevant_contexts, suggestions

    def _generate_suggestions(
        self,
        current_message: str,
        recent_contexts: List[Dict[str, Any]],
        language: str
    ) -> List[str]:
        """Generate contextual suggestions"""
        suggestions = []

        # Check for follow-up patterns
        if recent_contexts:
            last_context = recent_contexts[-1]
            last_intent = last_context.get('intent')

            # Suggest related actions
            if last_intent == 'create_task':
                if language == 'en':
                    suggestions.extend([
                        "Set a reminder for this task",
                        "Add more details to the task",
                        "Mark the task as high priority"
                    ])
                else:  # Urdu
                    suggestions.extend([
                        "اس کام کے لیے یاددہانی سیٹ کریں",
                        "کام میں مزید تفصیلات شامل کریں",
                        "کام کو اعلیٰ ترجیح کے طور پر نشان زد کریں"
                    ])

            elif last_intent == 'list_tasks':
                if language == 'en':
                    suggestions.extend([
                        "Show only high priority tasks",
                        "Filter tasks by due date",
                        "Mark a task as completed"
                    ])
                else:
                    suggestions.extend([
                        "صرف اعلیٰ ترجیحی کام دکھائیں",
                        "مقررہ تاریخ کے مطابق کام فلٹر کریں",
                        "کام کو مکمل شدہ کے طور پر نشان زد کریں"
                    ])

        # Check for pronoun references
        if self._contains_pronouns(current_message):
            # Look for entities in previous contexts
            for context in reversed(recent_contexts):
                if context.get('entities'):
                    # Suggest clarification if needed
                    if language == 'en':
                        suggestions.append("Referring to previous conversation")
                    else:
                        suggestions.append("پچھلی گفتگو کا حوالہ")
                    break

        return suggestions

    def _find_relevant_contexts(
        self,
        current_message: str,
        contexts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find contexts relevant to current message"""
        relevant = []

        current_keywords = self._extract_keywords(current_message.lower())

        for context in contexts:
            # Check for pronoun references
            if self._contains_pronouns(current_message):
                relevant.append(context)
                continue

            # Check for keyword overlap
            context_keywords = self._extract_keywords(
                context['user_message'].lower() + ' ' + context['assistant_response'].lower()
            )

            overlap = len(set(current_keywords) & set(context_keywords))
            if overlap > 0:
                relevant.append(context)

        return relevant

    def _determine_intent_with_context(
        self,
        current_message: str,
        recent_contexts: List[Dict[str, Any]]
    ) -> str:
        """Determine intent considering context"""
        # Check for follow-up patterns
        follow_up_patterns = ['yes', 'no', 'okay', 'sure', 'done', 'complete', 'finished']

        message_lower = current_message.lower()

        if any(pattern in message_lower for pattern in follow_up_patterns):
            if recent_contexts:
                last_intent = recent_contexts[-1].get('intent')
                # This is likely a follow-up to previous intent
                return f"follow_up_{last_intent}" if last_intent else "confirmation"

        # Check for pronouns indicating reference to previous context
        if self._contains_pronouns(current_message):
            return "contextual_reference"

        # Default: no specific context-based intent
        return "unknown"

    def _contains_pronouns(self, text: str) -> bool:
        """Check if text contains pronouns that might reference context"""
        pronouns = ['it', 'this', 'that', 'these', 'those', 'them', 'they']
        text_lower = text.lower()
        return any(f' {pronoun} ' in f' {text_lower} ' for pronoun in pronouns)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        import re
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in stop_words and len(w) > 3]

    def get_conversation_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get conversation summary for user"""
        from ..models.user_profile import ConversationContext
        from collections import Counter

        cutoff = datetime.now() - timedelta(days=days)

        contexts = self.db.query(ConversationContext).filter(
            ConversationContext.user_id == user_id,
            ConversationContext.timestamp >= cutoff
        ).all()

        if not contexts:
            return {
                'total_conversations': 0,
                'languages': {},
                'channels': {},
                'intents': {},
                'moods': {}
            }

        # Aggregate statistics
        languages = Counter([c.language for c in contexts])
        channels = Counter([c.channel for c in contexts])
        intents = Counter([c.intent for c in contexts if c.intent])
        moods = Counter([c.detected_mood for c in contexts if c.detected_mood])

        return {
            'total_conversations': len(contexts),
            'languages': dict(languages),
            'channels': dict(channels),
            'intents': dict(intents),
            'moods': dict(moods),
            'avg_conversations_per_day': len(contexts) / days,
            'most_common_intent': intents.most_common(1)[0][0] if intents else None,
            'most_common_mood': moods.most_common(1)[0][0] if moods else None
        }

    def clear_old_contexts(self, user_id: str, days: int = 30) -> int:
        """Clear old conversation contexts"""
        from ..models.user_profile import ConversationContext

        cutoff = datetime.now() - timedelta(days=days)

        deleted = self.db.query(ConversationContext).filter(
            ConversationContext.user_id == user_id,
            ConversationContext.timestamp < cutoff
        ).delete()

        self.db.commit()

        return deleted

    def get_mood_history(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get mood history for user"""
        from ..models.user_profile import ConversationContext

        cutoff = datetime.now() - timedelta(days=days)

        contexts = self.db.query(ConversationContext).filter(
            ConversationContext.user_id == user_id,
            ConversationContext.timestamp >= cutoff,
            ConversationContext.detected_mood.isnot(None)
        ).order_by(ConversationContext.timestamp).all()

        return [
            {
                'mood': c.detected_mood,
                'confidence': c.mood_confidence,
                'timestamp': c.timestamp,
                'channel': c.channel
            }
            for c in contexts
        ]

    def detect_conversation_patterns(self, user_id: str) -> Dict[str, Any]:
        """Detect patterns in user conversations"""
        summary = self.get_conversation_summary(user_id, days=30)

        patterns = {
            'preferred_language': max(summary['languages'].items(), key=lambda x: x[1])[0] if summary['languages'] else 'en',
            'preferred_channel': max(summary['channels'].items(), key=lambda x: x[1])[0] if summary['channels'] else 'text',
            'common_intents': [intent for intent, count in sorted(summary['intents'].items(), key=lambda x: x[1], reverse=True)[:5]],
            'conversation_frequency': summary['avg_conversations_per_day'],
            'is_active_user': summary['avg_conversations_per_day'] > 1.0
        }

        # Mood patterns
        mood_history = self.get_mood_history(user_id, days=30)
        if mood_history:
            from collections import Counter
            mood_counts = Counter([m['mood'] for m in mood_history])
            patterns['dominant_mood'] = mood_counts.most_common(1)[0][0]
            patterns['mood_variety'] = len(mood_counts)

        return patterns
