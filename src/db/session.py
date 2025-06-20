"""Database session management."""

import re
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, AsyncIterator, Optional

from sqlalchemy import event, text
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from config import get_config, get_logger

config = get_config()
logger = get_logger(__name__)

# Get database URL from config


def get_async_database_url(database_url: str) -> str:
    """Convert database URL to async format if needed.

    Args:
        database_url: Original database URL

    Returns:
        Database URL with async driver scheme
    """
    if not database_url:
        raise ValueError("DATABASE_URL is required")

    # Convert postgres:// or postgresql:// to postgresql+asyncpg://
    if database_url.startswith(("postgres://", "postgresql://")):
        # Replace the scheme with postgresql+asyncpg://
        async_url = re.sub(r"^postgres(ql)?://", "postgresql+asyncpg://", database_url)
        logger.info(
            "Converted database URL to async format: %s -> %s",
            database_url.split("@")[0] + "@...",
            async_url.split("@")[0] + "@...",
        )
        return async_url

    if database_url.startswith("postgresql+asyncpg://"):
        # Already in correct format
        return database_url

    if database_url.startswith("sqlite"):
        # For SQLite, use aiosqlite
        if database_url.startswith("sqlite://"):
            async_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
            logger.info("Converted SQLite URL to async format")
            return async_url

        if database_url.startswith("sqlite+aiosqlite://"):
            return database_url

    # If we can't determine the format, log a warning and return as-is
    logger.warning(
        "Could not determine async format for database URL: %s",
        database_url.split("@")[0] + "@..." if "@" in database_url else database_url,
    )
    return database_url


class AsyncSessionManager:
    def __init__(self, url: str, session_kwargs: Optional[dict[str, Any]] = None):
        if session_kwargs is None:
            session_kwargs = {}
        self._engine = create_async_engine(url, **session_kwargs)
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    def get_engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("AsyncSessionManager is not initialized")

        return self._engine

    async def close(self):
        if self._engine is None:
            raise RuntimeError("AsyncSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise RuntimeError("AsyncSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise RuntimeError("AsyncSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Configure the engine with connection pooling and retry settings
ASYNC_DATABASE_URL = get_async_database_url(config.DATABASE_URL)


# Configure engine settings based on database type
engine_kwargs: dict[str, Any] = {
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_reset_on_return": "rollback",  # Reset connection state on return to pool
    "echo": False,  # Disable SQL echo for cleaner logs
}

# Add pooling settings for non-SQLite databases
if not ASYNC_DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update(
        {
            "pool_size": 20,  # Maximum number of connections in the pool
            "max_overflow": 10,  # Maximum number of connections that can be created beyond pool_size
            "pool_timeout": 30,  # Timeout for getting a connection from the pool
            "pool_recycle": 1800,  # Recycle connections after 30 minutes
        }
    )
else:
    # For SQLite, use NullPool to avoid threading issues
    engine_kwargs["poolclass"] = NullPool

# Create session factory
session_manager = AsyncSessionManager(
    url=ASYNC_DATABASE_URL,
    session_kwargs=engine_kwargs,
)

session_engine = session_manager.get_engine()


@event.listens_for(session_engine.sync_engine, "connect")
def connect(dbapi_connection: DBAPIConnection, _connection_record):
    """Set up connection-level configuration."""
    logger.debug("New database connection established (id: %s)", dbapi_connection)


#     # For psycopg2, we need to handle connection setup differently
#     # if hasattr(dbapi_connection, "set_session"):
#     #     # Ensure we're in a clean state
#     #     dbapi_connection.set_session(readonly=False, autocommit=False)


# @event.listens_for(engine.sync_engine, "checkout")
# def checkout(
#     dbapi_connection: DBAPIConnection,
#     connection_record: ConnectionPoolEntry,
#     _connection_proxy: ConnectionPoolEntry,
# ):
#     """Perform health check on connection checkout."""
#     logger.debug(
#         "Checking out database connection (id: %d)",
#         id(dbapi_connection),
#     )
#     try:
#         # For psycopg2, execute a simple query to test the connection
#         cursor = dbapi_connection.cursor()
#         cursor.execute("SELECT 1")
#         cursor.close()
#     except Exception as e:
#         logger.warning(
#             "Connection health check failed (id: %d): %s",
#             id(dbapi_connection),
#             e,
#         )
#         connection_record.invalidate(e)
#         raise DisconnectionError() from e


# @event.listens_for(engine.sync_engine, "checkin")
# def checkin(dbapi_connection: DBAPIConnection, _connection_record: ConnectionPoolEntry):
#     """Log when a connection is checked back into the pool."""
#     logger.debug(
#         "Connection returned to pool (id: %d)",
#         id(dbapi_connection),
#     )


# @event.listens_for(engine.sync_engine, "reset")
# def reset(dbapi_connection: DBAPIConnection, _connection_record: ConnectionPoolEntry):
#     """Reset connection state."""
#     logger.debug(
#         "Connection reset (id: %d)",
#         id(dbapi_connection),
#     )
#     # # For psycopg2, ensure we reset the connection state
#     # if hasattr(dbapi_connection, "set_session"):
#     #     dbapi_connection.set_session(readonly=False, autocommit=False)


# @event.listens_for(engine.sync_engine, "invalidate")
# def invalidate(
#     dbapi_connection: DBAPIConnection,
#     _connection_record: ConnectionPoolEntry,
#     exception: SQLAlchemyError,
# ):
#     """Log when a connection is invalidated."""
#     logger.warning(
#         "Connection invalidated (id: %d) due to error: %s",
#         id(dbapi_connection),
#         exception,
#     )


async def get_session():
    async with session_manager.session() as session:
        yield session
