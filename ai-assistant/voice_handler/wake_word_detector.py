"""
Wake Word Detector
Detects wake words like "Hey Assistant" to activate voice commands
"""
import logging
import re
from typing import List, Optional
from .utils import is_urdu_speech

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Detects wake words in speech"""

    def __init__(self, custom_wake_words: Optional[List[str]] = None):
        """
        Initialize Wake Word Detector

        Args:
            custom_wake_words: List of custom wake words
        """
        # Default wake words
        self.wake_words = {
            'en': [
                'hey assistant',
                'ok assistant',
                'hello assistant',
                'hi assistant',
                'assistant',
            ],
            'ur': [
                'اے اسسٹنٹ',
                'ہیلو اسسٹنٹ',
                'سلام اسسٹنٹ',
                'اسسٹنٹ',
            ]
        }

        # Add custom wake words
        if custom_wake_words:
            for word in custom_wake_words:
                if is_urdu_speech(word):
                    self.wake_words['ur'].append(word.lower())
                else:
                    self.wake_words['en'].append(word.lower())

        self.last_detected = None
        self.detection_count = 0

        logger.info("Wake Word Detector initialized")

    def detect(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Detect wake word in text

        Args:
            text: Text to check

        Returns:
            Tuple of (detected, wake_word)
        """
        if not text:
            return False, None

        text_lower = text.lower()

        # Check English wake words
        for wake_word in self.wake_words['en']:
            if wake_word in text_lower:
                self.last_detected = wake_word
                self.detection_count += 1
                logger.info(f"Wake word detected: {wake_word}")
                return True, wake_word

        # Check Urdu wake words
        for wake_word in self.wake_words['ur']:
            if wake_word in text:
                self.last_detected = wake_word
                self.detection_count += 1
                logger.info(f"Wake word detected: {wake_word}")
                return True, wake_word

        return False, None

    def extract_command(self, text: str, wake_word: str) -> str:
        """
        Extract command after wake word

        Args:
            text: Full text with wake word
            wake_word: Detected wake word

        Returns:
            Command text without wake word
        """
        # Remove wake word from beginning of text
        text_lower = text.lower()
        wake_word_lower = wake_word.lower()

        # Try to find and remove wake word
        if wake_word_lower in text_lower:
            # Find position
            pos = text_lower.find(wake_word_lower)

            # Extract command (text after wake word)
            command = text[pos + len(wake_word):].strip()

            return command

        return text

    def add_wake_word(self, wake_word: str, language: Optional[str] = None):
        """
        Add custom wake word

        Args:
            wake_word: Wake word to add
            language: Language ('en' or 'ur', auto-detected if None)
        """
        wake_word_lower = wake_word.lower()

        if language is None:
            # Auto-detect language
            if is_urdu_speech(wake_word):
                language = 'ur'
            else:
                language = 'en'

        if wake_word_lower not in self.wake_words[language]:
            self.wake_words[language].append(wake_word_lower)
            logger.info(f"Added wake word: {wake_word} ({language})")

    def remove_wake_word(self, wake_word: str):
        """
        Remove wake word

        Args:
            wake_word: Wake word to remove
        """
        wake_word_lower = wake_word.lower()

        for language in ['en', 'ur']:
            if wake_word_lower in self.wake_words[language]:
                self.wake_words[language].remove(wake_word_lower)
                logger.info(f"Removed wake word: {wake_word}")
                return True

        return False

    def get_wake_words(self) -> dict:
        """
        Get all wake words

        Returns:
            Dictionary of wake words by language
        """
        return self.wake_words.copy()

    def get_stats(self) -> dict:
        """
        Get detection statistics

        Returns:
            Dictionary with stats
        """
        return {
            'detection_count': self.detection_count,
            'last_detected': self.last_detected,
            'total_wake_words': sum(len(words) for words in self.wake_words.values()),
            'wake_words_en': len(self.wake_words['en']),
            'wake_words_ur': len(self.wake_words['ur'])
        }

    def reset_stats(self):
        """Reset detection statistics"""
        self.detection_count = 0
        self.last_detected = None
        logger.info("Wake word stats reset")


class WakeWordValidator:
    """Validates and processes wake word commands"""

    def __init__(self):
        """Initialize validator"""
        self.command_patterns = {
            'en': [
                r'^(what|how|when|where|why|who|which)',  # Questions
                r'^(create|make|add|new)',  # Creation
                r'^(show|display|list|get)',  # Display
                r'^(send|message|call)',  # Communication
                r'^(open|start|run|execute)',  # Execution
                r'^(help|assist|explain)',  # Help
            ],
            'ur': [
                r'^(کیا|کیسے|کب|کہاں|کیوں|کون)',  # Questions
                r'^(بنائیں|بناؤ|شامل|نیا)',  # Creation
                r'^(دکھائیں|دکھاؤ|لسٹ)',  # Display
                r'^(بھیجیں|بھیجو|پیغام)',  # Communication
                r'^(کھولیں|شروع|چلائیں)',  # Execution
                r'^(مدد|وضاحت)',  # Help
            ]
        }

    def is_valid_command(self, command: str, language: str = 'en') -> bool:
        """
        Check if command is valid

        Args:
            command: Command text
            language: Language code

        Returns:
            True if command looks valid
        """
        if not command or len(command.strip()) < 3:
            return False

        command_lower = command.lower().strip()
        patterns = self.command_patterns.get(language, self.command_patterns['en'])

        # Check if command matches any pattern
        for pattern in patterns:
            if re.match(pattern, command_lower, re.IGNORECASE | re.UNICODE):
                return True

        # Also accept commands with enough words
        words = command_lower.split()
        if len(words) >= 2:
            return True

        return False

    def extract_intent(self, command: str, language: str = 'en') -> Optional[str]:
        """
        Extract intent from command

        Args:
            command: Command text
            language: Language code

        Returns:
            Intent string or None
        """
        command_lower = command.lower().strip()

        intent_keywords = {
            'en': {
                'create': ['create', 'make', 'add', 'new'],
                'list': ['show', 'display', 'list', 'get'],
                'send': ['send', 'message', 'whatsapp'],
                'execute': ['run', 'execute', 'open', 'start'],
                'help': ['help', 'assist', 'explain']
            },
            'ur': {
                'create': ['بنائیں', 'بناؤ', 'شامل'],
                'list': ['دکھائیں', 'دکھاؤ', 'لسٹ'],
                'send': ['بھیجیں', 'بھیجو', 'پیغام'],
                'execute': ['چلائیں', 'کھولیں', 'شروع'],
                'help': ['مدد', 'وضاحت']
            }
        }

        keywords = intent_keywords.get(language, intent_keywords['en'])

        for intent, intent_words in keywords.items():
            for word in intent_words:
                if word in command_lower:
                    return intent

        return None
