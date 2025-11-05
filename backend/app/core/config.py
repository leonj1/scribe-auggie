"""
Configuration management for the Audio Transcription Service.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Audio Transcription Service"
    debug: bool = False
    log_level: str = "INFO"
    
    # Google OAuth2
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(default="http://localhost:8000/auth/google/callback", env="GOOGLE_REDIRECT_URI")
    
    # JWT
    jwt_secret: str = Field(..., env="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Database
    mysql_url: str = Field(..., env="MYSQL_URL")
    
    # LLM Provider
    llm_api_key: str = Field(..., env="LLM_API_KEY")
    llm_provider: str = "requestyai"
    
    # Audio Storage
    audio_storage_path: str = Field(default="/tmp/audio_storage", env="AUDIO_STORAGE_PATH")
    max_chunk_size_mb: int = 10
    max_recording_duration_hours: int = 8
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "https://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
