from typing import Optional

from loguru import logger
from supabase import Client, create_client

from .settings import Settings


class SupabaseClient:
    _instance: Optional[Client] = None

    @classmethod
    def get_instance(cls, settings: Settings) -> Client:
        """Get or create Supabase client instance."""
        if cls._instance is None:
            try:
                cls._instance = create_client(settings.supabase.url, settings.supabase.key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.exception("Failed to initialize Supabase client")
                raise
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """Close Supabase client connection."""
        if cls._instance is not None:
            try:
                cls._instance.close()
                cls._instance = None
                logger.info("Supabase client closed successfully")
            except Exception as e:
                logger.exception("Failed to close Supabase client")
                raise
