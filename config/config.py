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
    SQLALCHEMY_URL: str = ""
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
