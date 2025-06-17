from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    url: str = Field(..., description="Database connection URL")
    echo: bool = Field(False, description="Enable SQL query logging")


class BotSettings(BaseModel):
    token: str = Field(..., description="Telegram bot token")
    admin_ids: list[int] = Field(default_factory=list, description="List of admin user IDs")


class UserbotSettings(BaseModel):
    api_id: int = Field(..., description="Telegram API ID")
    api_hash: str = Field(..., description="Telegram API hash")
    session_name: str = Field("userbot", description="Session name for Pyrogram")


class SupabaseSettings(BaseModel):
    url: str = Field(..., description="Supabase project URL")
    key: str = Field(..., description="Supabase API key")
    jwt_secret: str = Field(..., description="Supabase JWT secret")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application settings
    log_level: str = Field("INFO", description="Logging level")
    debug: bool = Field(False, description="Enable debug mode")

    # Database settings
    db: DatabaseSettings

    # Bot settings
    bot: BotSettings

    # Userbot settings
    userbot: UserbotSettings

    # Supabase settings
    supabase: SupabaseSettings


def load_settings() -> Settings:
    """Load settings from environment variables and .env file."""
    return Settings()
