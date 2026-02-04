"""
Application Configuration

Loads settings from environment variables with .env file support.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Explicitly load .env file from backend directory
_backend_dir = Path(__file__).parent.parent.parent
_env_file = _backend_dir / ".env"

if _env_file.exists():
    load_dotenv(_env_file, override=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "Agentic Assist"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./agentic_assist.db"
    
    # LLM - Gemini (Primary)
    GEMINI_API_KEY: Optional[str] = None
    
    # Auth
    SECRET_KEY: str = "your-super-secret-key-change-in-production-123456789"
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    
    @property
    def has_llm_configured(self) -> bool:
        """Check if LLM provider is configured."""
        return bool(self.GEMINI_API_KEY)
    
    @property
    def llm_provider(self) -> Optional[str]:
        """Get the configured LLM provider name."""
        if self.GEMINI_API_KEY:
            return "gemini"
        return None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Create singleton settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
