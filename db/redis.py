import json
from datetime import datetime
from typing import Any, Optional

import redis
from pydantic import BaseModel

from config import get_config, get_logger
from db.schemas import User

logger = get_logger(__name__)


class RedisClient:
    _instance: Optional[redis.Redis] = None
    _prefix = "telestories:"

    @classmethod
    def get_instance(cls) -> redis.Redis:
        """Get or create Redis client instance."""
        if cls._instance is None:
            config = get_config()
            try:
                kwargs = {
                    "host": config.REDIS_HOST,
                    "port": config.REDIS_PORT,
                    "db": config.REDIS_DB,
                    "decode_responses": True,
                }
                if config.REDIS_PASSWORD:
                    kwargs["password"] = config.REDIS_PASSWORD
                    logger.info(
                        "Initializing Redis client with password on %s:%d",
                        config.REDIS_HOST,
                        config.REDIS_PORT,
                    )
                else:
                    logger.info(
                        "Initializing Redis client on %s:%d", config.REDIS_HOST, config.REDIS_PORT
                    )

                cls._instance = redis.Redis(**kwargs)
                logger.info("Redis client initialized successfully")
            except Exception as e:
                logger.exception("Failed to initialize Redis client: %s", e)
                raise
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """Close Redis client connection."""
        if cls._instance is not None:
            try:
                cls._instance.close()
                cls._instance = None
                logger.info("Redis client closed successfully")
            except Exception as e:
                logger.exception("Failed to close Redis client: %s", e)
                raise

    @classmethod
    def get_key(cls, key: str) -> str:
        """Get prefixed key."""
        return f"{cls._prefix}{key}"


def get_cache() -> redis.Redis:
    """Get Redis client instance."""
    return RedisClient.get_instance()


class RedisModel(BaseModel):
    """Base model for Redis objects with serialization methods."""

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a value for Redis storage."""
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        return value

    def _deserialize_value(self, value: Any) -> Any:
        """Deserialize a value from Redis storage."""
        if isinstance(value, str) and value.count("T") == 1 and value.count("-") >= 2:
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return value
        if isinstance(value, dict):
            return {k: self._deserialize_value(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._deserialize_value(v) for v in value]
        return value

    def to_redis(self) -> str:
        """Convert model to Redis-compatible string."""
        data = self.model_dump()
        serialized_data = {k: self._serialize_value(v) for k, v in data.items()}
        return json.dumps(serialized_data)

    @classmethod
    def from_redis(cls, data: str):
        """Create model from Redis-compatible string."""
        if not data:
            return None
        json_data = json.loads(data)
        deserialized_data = {k: cls._deserialize_value(cls, v) for k, v in json_data.items()}
        return cls.model_validate(deserialized_data)


class CachedUser(User, RedisModel):
    """User model with Redis caching capabilities."""

    @classmethod
    def get_cache_key(cls, user_id: int) -> str:
        """Get Redis key for user."""
        return RedisClient.get_key(f"user:{user_id}")

    @classmethod
    def get_from_cache(cls, user_id: int) -> Optional["CachedUser"]:
        """Get user from Redis cache."""
        redis_client = get_cache()
        key = cls.get_cache_key(user_id)
        data = redis_client.get(key)
        if data:
            logger.info("Retrieved user from cache with key %s", key)
        else:
            logger.info("Cache miss for user with key %s", key)
        return cls.from_redis(data) if data else None

    def save_to_cache(self, expire_seconds: int = 3600) -> None:
        """Save user to Redis cache."""
        redis_client = get_cache()
        key = self.get_cache_key(self.id)
        redis_client.setex(key, expire_seconds, self.to_redis())
        logger.info("Saved user to cache with key %s (expires in %d seconds)", key, expire_seconds)

    @classmethod
    def delete_from_cache(cls, user_id: int) -> None:
        """Delete user from Redis cache."""
        redis_client = get_cache()
        key = cls.get_cache_key(user_id)
        result = redis_client.delete(key)
        if result:
            logger.info("Deleted user from cache with key %s", key)
        else:
            logger.info("No user found in cache with key %s", key)
