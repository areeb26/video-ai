from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/video_ai_db"

    # Google AI / Veo Configuration
    GOOGLE_AI_API_KEY: str = ""
    GOOGLE_AI_BEARER_TOKEN: str = ""  # OAuth bearer token for Veo 3.1
    VEO_PROJECT_ID: str = ""  # Your Google project ID

    # Application
    SECRET_KEY: str = "your-secret-key-change-this"
    DEBUG: bool = True
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MEDIA_DIR: str = "./media"
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB

    # Video Settings
    DEFAULT_VIDEO_QUALITY: str = "low"
    MAX_FACE_EMBEDDINGS: int = 10
    MIN_FACE_EMBEDDINGS: int = 3

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Veo Character Consistency"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
