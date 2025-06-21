"""Database session management."""

import re
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Optional

from sqlalchemy import event
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

log = get_logger(__name__)

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
        log.info(
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
            log.info("Converted SQLite URL to async format")
            return async_url

        if database_url.startswith("sqlite+aiosqlite://"):
            return database_url

    # If we can't determine the format, log a warning and return as-is
    log.warning(
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
            raise SQLAlchemyError("AsyncEngine is not initialized")

        return self._engine

    async def close(self):
        if self._engine is None:
            raise SQLAlchemyError("AsyncEngine is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise SQLAlchemyError("AsyncEngine is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception as e:
                log.exception("Error in connection: %s", e)
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise SQLAlchemyError("AsyncSessionMaker is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception as e:
            log.exception("Error in session: %s", e)
            await session.rollback()
            raise
        finally:
            await session.close()
            log.debug("Session closed")


# Configure the engine with connection pooling and retry settings
DATABASE_URL = get_async_database_url(get_config().DATABASE_URL)


# Configure engine settings based on database type
engine_kwargs: dict[str, Any] = {
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_reset_on_return": "rollback",  # Reset connection state on return to pool
    "echo": False,  # Disable SQL echo for cleaner logs
}

# Add pooling settings for non-SQLite databases
if not DATABASE_URL.startswith("sqlite"):
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
    url=DATABASE_URL,
    session_kwargs=engine_kwargs,
)

session_engine = session_manager.get_engine()


@event.listens_for(session_engine.sync_engine, "connect")
def connect(dbapi_connection: DBAPIConnection, _connection_record: Any) -> None:
    """Set up connection-level configuration."""
    log.debug("New database connection established: %s", dbapi_connection)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        yield session
