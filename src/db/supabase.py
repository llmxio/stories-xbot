from typing import Optional

from supabase import Client, create_client

from config import Config, get_logger

LOGGER = get_logger(__name__)


class SupabaseClient:
    _instance: Optional[Client] = None

    @classmethod
    def get_instance(cls, config: Config) -> Client:
        """Get or create Supabase client instance."""
        if cls._instance is None:
            try:
                cls._instance = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
                LOGGER.info("Supabase client initialized successfully")
            except Exception as e:
                LOGGER.exception("Failed to initialize Supabase client: %s", e)
                raise
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """Close Supabase client connection."""
        if cls._instance is not None:
            try:
                cls._instance.close()  # type: ignore[attr-defined]
                cls._instance = None
                LOGGER.info("Supabase client closed successfully")
            except Exception as e:
                LOGGER.exception("Failed to close Supabase client: %s", e)
                raise
