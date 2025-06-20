from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # Example fields, adapt as needed for your project
    BOT_TOKEN: str = ""
    USERBOT_API_ID: int = 0
    USERBOT_API_HASH: str = ""
    USERBOT_PHONE_NUMBER: str = ""
    USERBOT_SESSION_NAME: str = "userbot"  # Session name for userbot
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    DATABASE_URL: str = ""
    BOT_ADMIN_ID: int = 0
    LOG_LEVEL: str = "DEBUG"  # Logging level, e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""  # Optional Redis password

    # Add more fields as needed

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_config() -> Config:
    return Config()
