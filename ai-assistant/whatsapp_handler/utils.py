"""
Utility functions for WhatsApp handler
"""
import re
from typing import Optional
from datetime import datetime


def format_phone_number(number: str, country_code: str = "+92") -> str:
    """
    Format phone number for WhatsApp

    Args:
        number: Phone number (can include country code or not)
        country_code: Default country code (default: +92 for Pakistan)

    Returns:
        Formatted phone number with country code
    """
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', number)

    # If already has country code
    if cleaned.startswith('92') and len(cleaned) == 12:
        return '+' + cleaned
    elif cleaned.startswith('1') and len(cleaned) == 11:  # US number
        return '+' + cleaned

    # Add default country code
    if cleaned.startswith('0'):
        cleaned = cleaned[1:]  # Remove leading 0

    # Remove country code prefix if exists
    country_digits = country_code.replace('+', '')
    if cleaned.startswith(country_digits):
        cleaned = cleaned[len(country_digits):]

    return f"{country_code}{cleaned}"


def is_valid_phone_number(number: str) -> bool:
    """
    Validate phone number format

    Args:
        number: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', number)

    # Check length (10-15 digits)
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False

    return True


def sanitize_message(message: str) -> str:
    """
    Sanitize message for WhatsApp

    Args:
        message: Message to sanitize

    Returns:
        Sanitized message
    """
    # Remove any potential XSS or injection attempts
    # Keep Unicode for Urdu support
    return message.strip()


def parse_whatsapp_time(time_str: str) -> Optional[datetime]:
    """
    Parse WhatsApp timestamp

    Args:
        time_str: Time string from WhatsApp

    Returns:
        datetime object or None
    """
    try:
        # Try different formats
        formats = [
            "%I:%M %p",  # 12:30 PM
            "%H:%M",     # 14:30
            "%d/%m/%Y, %I:%M %p",  # 15/11/2025, 2:30 PM
        ]

        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue

        return None
    except Exception:
        return None


def extract_command_from_message(message: str, language: str = 'en') -> Optional[dict]:
    """
    Extract command from WhatsApp message

    Args:
        message: Message text
        language: Language code

    Returns:
        Dictionary with command details or None
    """
    message = message.strip().lower()

    # Command patterns
    patterns = {
        'create_task': [
            r'create task (.+)',
            r'add task (.+)',
            r'کام بنائیں (.+)',
            r'ٹاسک بنائیں (.+)',
        ],
        'list_tasks': [
            r'list tasks?',
            r'show tasks?',
            r'کام دکھائیں',
            r'ٹاسک لسٹ',
        ],
        'help': [
            r'help',
            r'مدد',
            r'commands?',
            r'کمانڈز',
        ],
    }

    for command, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, message, re.IGNORECASE | re.UNICODE)
            if match:
                return {
                    'command': command,
                    'args': match.group(1) if match.groups() else None,
                    'language': language
                }

    return None


def is_authorized_number(number: str, authorized_numbers: list) -> bool:
    """
    Check if phone number is authorized

    Args:
        number: Phone number to check
        authorized_numbers: List of authorized numbers

    Returns:
        True if authorized, False otherwise
    """
    formatted = format_phone_number(number)

    for auth_number in authorized_numbers:
        if format_phone_number(auth_number) == formatted:
            return True

    return False


def create_whatsapp_web_url(number: str, message: str = "") -> str:
    """
    Create WhatsApp Web URL for sending message

    Args:
        number: Phone number
        message: Pre-filled message (optional)

    Returns:
        WhatsApp Web URL
    """
    formatted = format_phone_number(number).replace('+', '')

    if message:
        from urllib.parse import quote
        encoded_message = quote(message)
        return f"https://web.whatsapp.com/send?phone={formatted}&text={encoded_message}"

    return f"https://web.whatsapp.com/send?phone={formatted}"


def detect_language_from_message(message: str) -> str:
    """
    Detect language from message content

    Args:
        message: Message text

    Returns:
        Language code ('en' or 'ur')
    """
    # Count Urdu characters (Arabic script)
    urdu_chars = len(re.findall(r'[\u0600-\u06FF]', message))

    # If more than 30% Urdu characters, consider it Urdu
    if len(message) > 0 and urdu_chars / len(message) > 0.3:
        return 'ur'

    return 'en'


def format_task_list_for_whatsapp(tasks: list, language: str = 'en') -> str:
    """
    Format task list for WhatsApp message

    Args:
        tasks: List of task dictionaries
        language: Language code

    Returns:
        Formatted message
    """
    if language == 'ur':
        if not tasks:
            return "کوئی کام نہیں ملا۔"

        message = "*آپ کے کام:*\n\n"
        for i, task in enumerate(tasks, 1):
            status_emoji = "✅" if task.get('status') == 'completed' else "⏳"
            message += f"{i}. {status_emoji} {task.get('title', 'N/A')}\n"
            if task.get('due_date'):
                message += f"   تاریخ: {task.get('due_date')}\n"

        return message
    else:
        if not tasks:
            return "No tasks found."

        message = "*Your Tasks:*\n\n"
        for i, task in enumerate(tasks, 1):
            status_emoji = "✅" if task.get('status') == 'completed' else "⏳"
            message += f"{i}. {status_emoji} {task.get('title', 'N/A')}\n"
            if task.get('due_date'):
                message += f"   Due: {task.get('due_date')}\n"

        return message


def create_help_message(language: str = 'en') -> str:
    """
    Create help message for WhatsApp

    Args:
        language: Language code

    Returns:
        Help message
    """
    if language == 'ur':
        return """*AI معاون - مدد*

*کام:*
• کام بنائیں [تفصیل]
• میرے کام دکھائیں
• کام مکمل کریں [نمبر]

*فائلیں:*
• فائل بنائیں [نام]
• فائل پڑھیں [نام]

*دیگر:*
• مدد - یہ پیغام دکھائیں

مزید معلومات کے لیے http://localhost:8001 دیکھیں"""
    else:
        return """*AI Assistant - Help*

*Tasks:*
• create task [description]
• list my tasks
• complete task [number]

*Files:*
• create file [name]
• read file [name]

*Other:*
• help - Show this message

For more info visit http://localhost:8001"""
