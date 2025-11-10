"""
Bilingual NLP Processor (English/Urdu)
Processes natural language commands and extracts intent
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json


class BilingualNLPProcessor:
    """Natural Language Processing for English and Urdu commands"""

    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.entity_extractors = self._load_entity_extractors()

    def _load_intent_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load intent patterns for both languages"""
        return {
            "create_task": [
                # English patterns
                {"pattern": r"create\s+(?:a\s+)?task\s+(.+)", "lang": "en"},
                {"pattern": r"add\s+(?:a\s+)?task\s+(.+)", "lang": "en"},
                {"pattern": r"remind\s+me\s+to\s+(.+)", "lang": "en"},
                {"pattern": r"todo:\s*(.+)", "lang": "en"},
                # Urdu patterns
                {"pattern": r"کام\s+بنائیں\s+(.+)", "lang": "ur"},
                {"pattern": r"ٹاسک\s+بنائیں\s+(.+)", "lang": "ur"},
                {"pattern": r"یاد\s+دلائیں\s+(.+)", "lang": "ur"},
            ],
            "list_tasks": [
                # English
                {"pattern": r"(?:show|list|display)\s+(?:my\s+)?tasks?", "lang": "en"},
                {"pattern": r"what\s+(?:are\s+)?my\s+tasks?", "lang": "en"},
                {"pattern": r"tasks?\s+list", "lang": "en"},
                # Urdu
                {"pattern": r"کام\s+دکھائیں", "lang": "ur"},
                {"pattern": r"ٹاسک\s+لسٹ", "lang": "ur"},
                {"pattern": r"میرے\s+کام", "lang": "ur"},
            ],
            "complete_task": [
                # English
                {"pattern": r"complete\s+task\s+(.+)", "lang": "en"},
                {"pattern": r"mark\s+(.+)\s+as\s+(?:done|completed)", "lang": "en"},
                {"pattern": r"done\s+with\s+(.+)", "lang": "en"},
                # Urdu
                {"pattern": r"کام\s+مکمل\s+(.+)", "lang": "ur"},
                {"pattern": r"ختم\s+کریں\s+(.+)", "lang": "ur"},
            ],
            "file_create": [
                # English
                {"pattern": r"create\s+(?:a\s+)?file\s+(?:named\s+)?(.+)", "lang": "en"},
                {"pattern": r"make\s+(?:a\s+)?file\s+(.+)", "lang": "en"},
                {"pattern": r"new\s+file\s+(.+)", "lang": "en"},
                # Urdu
                {"pattern": r"فائل\s+بنائیں\s+(.+)", "lang": "ur"},
                {"pattern": r"نئی\s+فائل\s+(.+)", "lang": "ur"},
            ],
            "file_read": [
                # English
                {"pattern": r"read\s+(?:the\s+)?file\s+(.+)", "lang": "en"},
                {"pattern": r"show\s+(?:me\s+)?(?:the\s+)?file\s+(.+)", "lang": "en"},
                {"pattern": r"open\s+(.+)", "lang": "en"},
                # Urdu
                {"pattern": r"فائل\s+پڑھیں\s+(.+)", "lang": "ur"},
                {"pattern": r"دکھائیں\s+(.+)", "lang": "ur"},
            ],
            "file_edit": [
                # English
                {"pattern": r"edit\s+(?:the\s+)?file\s+(.+)", "lang": "en"},
                {"pattern": r"modify\s+(.+)", "lang": "en"},
                {"pattern": r"update\s+(.+)", "lang": "en"},
                # Urdu
                {"pattern": r"فائل\s+تبدیل\s+کریں\s+(.+)", "lang": "ur"},
                {"pattern": r"ایڈٹ\s+کریں\s+(.+)", "lang": "ur"},
            ],
            "execute_command": [
                # English
                {"pattern": r"run\s+command\s+(.+)", "lang": "en"},
                {"pattern": r"execute\s+(.+)", "lang": "en"},
                {"pattern": r"command:\s*(.+)", "lang": "en"},
                # Urdu
                {"pattern": r"کمانڈ\s+چلائیں\s+(.+)", "lang": "ur"},
                {"pattern": r"رن\s+کریں\s+(.+)", "lang": "ur"},
            ],
            "trigger_n8n": [
                # English
                {"pattern": r"trigger\s+(?:n8n\s+)?workflow\s+(.+)", "lang": "en"},
                {"pattern": r"run\s+(?:n8n\s+)?workflow\s+(.+)", "lang": "en"},
                {"pattern": r"execute\s+workflow\s+(.+)", "lang": "en"},
                # Urdu
                {"pattern": r"ورک\s*فلو\s+چلائیں\s+(.+)", "lang": "ur"},
                {"pattern": r"n8n\s+چلائیں\s+(.+)", "lang": "ur"},
            ],
            "send_email": [
                # English
                {"pattern": r"send\s+(?:an\s+)?email\s+to\s+(.+)", "lang": "en"},
                {"pattern": r"email\s+(.+)", "lang": "en"},
                # Urdu
                {"pattern": r"ای\s*میل\s+بھیجیں\s+(.+)", "lang": "ur"},
            ],
            "search": [
                # English
                {"pattern": r"search\s+(?:for\s+)?(.+)", "lang": "en"},
                {"pattern": r"find\s+(.+)", "lang": "en"},
                {"pattern": r"look\s+for\s+(.+)", "lang": "en"},
                # Urdu
                {"pattern": r"تلاش\s+کریں\s+(.+)", "lang": "ur"},
                {"pattern": r"ڈھونڈیں\s+(.+)", "lang": "ur"},
            ],
            "send_whatsapp": [
                # English
                {"pattern": r"send\s+(?:a\s+)?whatsapp\s+(?:message\s+)?to\s+(.+)", "lang": "en"},
                {"pattern": r"whatsapp\s+(.+)", "lang": "en"},
                {"pattern": r"message\s+(.+)\s+on\s+whatsapp", "lang": "en"},
                # Urdu
                {"pattern": r"واٹس\s*ایپ\s+(?:پیغام\s+)?بھیجیں\s+(.+)", "lang": "ur"},
                {"pattern": r"واٹس\s*ایپ\s+(.+)", "lang": "ur"},
            ],
            "schedule_whatsapp": [
                # English
                {"pattern": r"schedule\s+whatsapp\s+(?:message\s+)?to\s+(.+)", "lang": "en"},
                {"pattern": r"send\s+whatsapp\s+later\s+to\s+(.+)", "lang": "en"},
                # Urdu
                {"pattern": r"واٹس\s*ایپ\s+وقت\s+پر\s+بھیجیں\s+(.+)", "lang": "ur"},
            ],
        }

    def _load_entity_extractors(self) -> Dict[str, List[str]]:
        """Load entity extraction patterns"""
        return {
            "date_patterns": [
                r"(?:on\s+)?(\d{4}-\d{2}-\d{2})",
                r"(?:on\s+)?(today|tomorrow|yesterday)",
                r"(?:on\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
                r"in\s+(\d+)\s+(day|days|hour|hours|minute|minutes)",
            ],
            "priority_patterns": [
                r"(low|medium|high|urgent)\s+priority",
                r"priority:\s*(low|medium|high|urgent)",
            ],
            "file_patterns": [
                r"file\s+(?:named\s+)?['\"]?([^\s'\"]+)['\"]?",
                r"['\"]([^'\"]+\.(?:txt|md|json|csv|pdf|doc|docx|py|js|html|css))['\"]",
            ],
        }

    def process(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Process natural language input and extract intent & entities

        Args:
            text: Input text in English or Urdu
            language: Language code (en or ur)

        Returns:
            Dictionary containing intent, entities, and metadata
        """
        text_lower = text.lower()

        # Detect language if auto
        detected_lang = self._detect_language(text)
        if language == "auto":
            language = detected_lang

        # Extract intent
        intent, confidence, extracted_data = self._extract_intent(text_lower, language)

        # Extract entities
        entities = self._extract_entities(text, intent)

        # Extract time-based entities
        time_entities = self._extract_time_entities(text)

        return {
            "intent": intent,
            "confidence": confidence,
            "language": language,
            "detected_language": detected_lang,
            "entities": {**entities, **time_entities},
            "extracted_data": extracted_data,
            "original_text": text,
        }

    def _detect_language(self, text: str) -> str:
        """Detect if text is in Urdu or English"""
        # Simple detection based on Urdu characters
        urdu_chars = re.findall(r'[\u0600-\u06FF]', text)
        if len(urdu_chars) > len(text) * 0.3:
            return "ur"
        return "en"

    def _extract_intent(self, text: str, language: str) -> Tuple[str, float, Optional[str]]:
        """Extract intent from text"""
        for intent, patterns in self.intent_patterns.items():
            for pattern_dict in patterns:
                # Match language-specific patterns
                if pattern_dict["lang"] == language or pattern_dict["lang"] == "both":
                    match = re.search(pattern_dict["pattern"], text, re.IGNORECASE)
                    if match:
                        extracted = match.group(1) if match.groups() else None
                        return intent, 0.9, extracted

        return "unknown", 0.0, None

    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """Extract entities from text based on intent"""
        entities = {}

        # Extract priority
        for pattern in self.entity_extractors["priority_patterns"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities["priority"] = match.group(1).lower()

        # Extract file paths/names
        if "file" in intent:
            for pattern in self.entity_extractors["file_patterns"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities["file_path"] = match.group(1)
                    break

        return entities

    def _extract_time_entities(self, text: str) -> Dict[str, Any]:
        """Extract time-related entities"""
        time_entities = {}

        # Extract dates
        for pattern in self.entity_extractors["date_patterns"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                parsed_date = self._parse_date_string(date_str)
                if parsed_date:
                    time_entities["due_date"] = parsed_date.isoformat()

        return time_entities

    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parse natural language date strings"""
        date_str_lower = date_str.lower()

        if date_str_lower == "today":
            return datetime.now()
        elif date_str_lower == "tomorrow":
            return datetime.now() + timedelta(days=1)
        elif date_str_lower == "yesterday":
            return datetime.now() - timedelta(days=-1)

        # Try ISO format
        try:
            return datetime.fromisoformat(date_str)
        except:
            pass

        # Try to parse "in X days/hours"
        match = re.search(r"(\d+)\s+(day|days|hour|hours|minute|minutes)", date_str_lower)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)

            if "day" in unit:
                return datetime.now() + timedelta(days=amount)
            elif "hour" in unit:
                return datetime.now() + timedelta(hours=amount)
            elif "minute" in unit:
                return datetime.now() + timedelta(minutes=amount)

        return None

    def generate_response(self, intent: str, language: str, data: Any = None) -> str:
        """Generate natural language response based on intent and language"""
        responses = {
            "en": {
                "create_task": "Task created successfully!",
                "list_tasks": "Here are your tasks:",
                "complete_task": "Task marked as completed!",
                "file_create": "File created successfully!",
                "file_read": "Here's the file content:",
                "file_edit": "File updated successfully!",
                "execute_command": "Command executed successfully!",
                "trigger_n8n": "Workflow triggered successfully!",
                "send_email": "Email sent successfully!",
                "send_whatsapp": "WhatsApp message sent successfully!",
                "schedule_whatsapp": "WhatsApp message scheduled successfully!",
                "search": "Here are the search results:",
                "unknown": "I'm not sure what you want me to do. Can you please rephrase?",
                "error": "An error occurred: {error}",
            },
            "ur": {
                "create_task": "کام کامیابی سے بنایا گیا!",
                "list_tasks": "یہ آپ کے کام ہیں:",
                "complete_task": "کام مکمل کر دیا گیا!",
                "file_create": "فائل کامیابی سے بنائی گئی!",
                "file_read": "فائل کا مواد:",
                "file_edit": "فائل اپ ڈیٹ ہو گئی!",
                "execute_command": "کمانڈ چل گئی!",
                "trigger_n8n": "ورک فلو شروع ہو گیا!",
                "send_email": "ای میل بھیج دی گئی!",
                "send_whatsapp": "واٹس ایپ پیغام بھیج دیا گیا!",
                "schedule_whatsapp": "واٹس ایپ پیغام شیڈول ہو گیا!",
                "search": "تلاش کے نتائج:",
                "unknown": "مجھے سمجھ نہیں آیا۔ برائے مہربانی دوبارہ بتائیں؟",
                "error": "ایک خرابی واقع ہوئی: {error}",
            },
        }

        return responses.get(language, responses["en"]).get(intent, responses[language]["unknown"])
