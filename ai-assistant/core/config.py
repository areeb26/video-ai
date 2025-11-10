"""
AI Assistant Configuration
Manages environment variables and application settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Application
    APP_NAME: str = "AI Multitask Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8001"]

    # Database
    DATABASE_PATH: str = "ai-assistant/database/assistant.db"

    # N8N Integration
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook"
    N8N_API_URL: str = "http://localhost:5678/api/v1"
    N8N_API_KEY: str = ""

    # Language Settings
    DEFAULT_LANGUAGE: str = "en"  # en or ur
    SUPPORTED_LANGUAGES: List[str] = ["en", "ur"]

    # File Operations
    WORKSPACE_DIR: str = os.path.expanduser("~/ai-assistant-workspace")
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS: List[str] = [
        ".txt", ".md", ".json", ".csv", ".pdf",
        ".doc", ".docx", ".py", ".js", ".html", ".css"
    ]

    # System Commands
    ENABLE_SYSTEM_COMMANDS: bool = True
    SAFE_COMMANDS: List[str] = [
        "ls", "pwd", "date", "whoami", "cat", "echo",
        "mkdir", "touch", "cp", "mv", "grep", "find"
    ]
    BLOCKED_COMMANDS: List[str] = [
        "rm -rf", "sudo", "shutdown", "reboot",
        "mkfs", "dd", "chmod 777", "> /dev/sda"
    ]

    # Task Management
    TASK_REMINDER_INTERVAL: int = 3600  # seconds
    MAX_TASKS_PER_USER: int = 100

    # Email Settings (optional)
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    # Calendar Integration (optional)
    CALENDAR_PROVIDER: str = "google"  # google, outlook, etc.
    CALENDAR_API_KEY: str = ""

    # AI/NLP Settings
    USE_LOCAL_NLP: bool = True
    OPENAI_API_KEY: str = ""  # Optional for enhanced NLP

    # WhatsApp Integration
    WHATSAPP_ENABLED: bool = True
    WHATSAPP_METHOD: str = "selenium"  # selenium or simple
    WHATSAPP_SESSION_DIR: str = os.path.expanduser("~/.ai-assistant/whatsapp-session")
    WHATSAPP_HEADLESS: bool = False  # Run browser in headless mode
    WHATSAPP_DEFAULT_COUNTRY_CODE: str = "+92"  # Default country code for Pakistan
    WHATSAPP_QUEUE_CHECK_INTERVAL: int = 30  # seconds
    WHATSAPP_AUTO_START_QUEUE: bool = False  # Auto-start queue worker on startup
    WHATSAPP_AUTHORIZED_NUMBERS: List[str] = []  # List of authorized numbers

    # Voice Integration
    VOICE_ENABLED: bool = True
    VOICE_WAKE_WORD_REQUIRED: bool = True  # Require wake word before commands
    VOICE_WAKE_WORDS: List[str] = ["hey assistant", "اے اسسٹنٹ"]  # Custom wake words
    VOICE_CONTINUOUS_MODE: bool = False  # Continue listening after command
    VOICE_RESPONSE_ENABLED: bool = True  # Enable voice responses
    VOICE_SPEECH_RATE: int = 150  # Speech rate (words per minute)
    VOICE_VOLUME: float = 0.9  # Volume level (0.0 to 1.0)
    VOICE_ENERGY_THRESHOLD: int = 4000  # Microphone energy threshold
    VOICE_TIMEOUT: int = 5  # Listening timeout in seconds
    VOICE_PHRASE_TIME_LIMIT: int = 10  # Maximum phrase duration
    VOICE_AUTO_CALIBRATE: bool = True  # Auto-calibrate microphone on startup

    # Smart Learning & Personalization
    LEARNING_ENABLED: bool = True  # Enable smart learning features
    LEARNING_MIN_PATTERN_OCCURRENCES: int = 3  # Minimum occurrences to detect pattern
    LEARNING_CONFIDENCE_THRESHOLD: float = 0.6  # Minimum confidence for patterns
    LEARNING_HABIT_THRESHOLD: float = 0.7  # Minimum confidence to save as habit
    LEARNING_AUTO_LEARN: bool = True  # Automatically learn from user actions
    LEARNING_CONTEXT_WINDOW: int = 10  # Number of previous conversations to consider
    LEARNING_CONTEXT_TIMEOUT_MINUTES: int = 30  # Context expires after minutes
    LEARNING_PREDICTION_LIMIT: int = 5  # Max number of predictions to show
    LEARNING_VOICE_RECOGNITION_THRESHOLD: float = 0.75  # Min confidence for voice recognition

    class Config:
        env_file = "ai-assistant/.env"
        case_sensitive = True


# Global settings instance
settings = Settings()


# Create workspace directory if it doesn't exist
os.makedirs(settings.WORKSPACE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)
