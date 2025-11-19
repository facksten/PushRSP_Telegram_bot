"""
Configuration module for PushTutor bot
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Telegram Userbot
    telegram_api_id: Optional[int] = Field(None, alias="TELEGRAM_API_ID")
    telegram_api_hash: Optional[str] = Field(None, alias="TELEGRAM_API_HASH")
    telegram_phone: Optional[str] = Field(None, alias="TELEGRAM_PHONE")
    
    # Bot API
    bot_token: Optional[str] = Field(None, alias="BOT_TOKEN")
    
    # Admin Configuration
    admin_ids: List[int] = Field(default_factory=list, alias="ADMIN_IDS")
    
    # LLM API Keys
    gemini_api_key: Optional[str] = Field(None, alias="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    openrouter_api_key: Optional[str] = Field(None, alias="OPENROUTER_API_KEY")
    
    # TGStat API
    tgstat_api_key: Optional[str] = Field(None, alias="TGSTAT_API_KEY")
    
    # Database
    database_url: str = Field("sqlite:///pushtutor.db", alias="DATABASE_URL")
    
    # Logging
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_file: str = Field("logs/pushtutor.log", alias="LOG_FILE")
    
    # LangChain
    default_llm_provider: str = Field("gemini", alias="DEFAULT_LLM_PROVIDER")
    default_model: str = Field("gemini-1.5-pro", alias="DEFAULT_MODEL")
    
    # Feature Flags
    enable_userbot: bool = Field(True, alias="ENABLE_USERBOT")
    enable_bot: bool = Field(True, alias="ENABLE_BOT")
    enable_vector_search: bool = Field(False, alias="ENABLE_VECTOR_SEARCH")
    
    @validator("admin_ids", pre=True)
    def parse_admin_ids(cls, v):
        """Parse comma-separated admin IDs"""
        if isinstance(v, str):
            if not v.strip():
                return []
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        if isinstance(v, int):
            return [v]
        if isinstance(v, list):
            return v
        return []
    
    @validator("enable_userbot", "enable_bot", "enable_vector_search", pre=True)
    def parse_bool(cls, v):
        """Parse boolean values from string"""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Runtime configuration storage (for admin updates)
class RuntimeConfig:
    """Runtime configuration that can be modified by admins"""
    
    def __init__(self):
        self._config = {
            "bot_enabled": True,
            "userbot_enabled": True,
            "current_llm_provider": settings.default_llm_provider,
            "current_model": settings.default_model,
            "admin_notifications": True,
        }
    
    def get(self, key: str, default=None):
        return self._config.get(key, default)
    
    def set(self, key: str, value):
        self._config[key] = value
    
    def get_all(self) -> dict:
        return self._config.copy()


runtime_config = RuntimeConfig()
