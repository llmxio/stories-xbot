"""Database session management."""

import re
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from config.config import get_config
from config.logger import get_logger

logger = get_logger(__name__)

# Get database URL from config
config = get_config()


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
    elif database_url.startswith("postgresql+asyncpg://"):
        # Already in correct format
        return database_url
    elif database_url.startswith("sqlite"):
        # For SQLite, use aiosqlite
        if database_url.startswith("sqlite://"):
            async_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
            logger.info("Converted SQLite URL to async format")
            return async_url
        elif database_url.startswith("sqlite+aiosqlite://"):
            return database_url

    # If we can't determine the format, log a warning and return as-is
    logger.warning(
        "Could not determine async format for database URL: %s",
        database_url.split("@")[0] + "@..." if "@" in database_url else database_url,
    )
    return database_url


# Configure the engine with connection pooling and retry settings
async_database_url = get_async_database_url(config.DATABASE_URL)

# Configure engine settings based on database type
engine_kwargs = {
    "pool_pre_ping": True,  # Enable connection health checks
    "pool_reset_on_return": "rollback",  # Reset connection state on return to pool
    "echo": False,  # Disable SQL echo for cleaner logs
}

# Add pooling settings for non-SQLite databases
if not async_database_url.startswith("sqlite"):
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

engine = create_async_engine(async_database_url, **engine_kwargs)

# Create session factory
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# @event.listens_for(Engine, "connect")
# def connect(dbapi_connection, connection_record):
#     """Set up connection-level configuration."""
#     logger.debug(
#         "New database connection established (id: %d)",
#         id(dbapi_connection),
#     )
#     # For psycopg2, we need to handle connection setup differently
#     if hasattr(dbapi_connection, "set_session"):
#         # Ensure we're in a clean state
#         dbapi_connection.set_session(readonly=False, autocommit=False)


# @event.listens_for(Engine, "checkout")
# def checkout(dbapi_connection, connection_record, connection_proxy):
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


# @event.listens_for(Engine, "checkin")
# def checkin(dbapi_connection, connection_record):
#     """Log when a connection is checked back into the pool."""
#     logger.debug(
#         "Connection returned to pool (id: %d)",
#         id(dbapi_connection),
#     )


# @event.listens_for(Engine, "reset")
# def reset(dbapi_connection, connection_record):
#     """Reset connection state."""
#     logger.debug(
#         "Connection reset (id: %d)",
#         id(dbapi_connection),
#     )
#     # For psycopg2, ensure we reset the connection state
#     if hasattr(dbapi_connection, "set_session"):
#         dbapi_connection.set_session(readonly=False, autocommit=False)


# @event.listens_for(Engine, "invalidate")
# def invalidate(dbapi_connection, _connection_record, exception):
#     """Log when a connection is invalidated."""
#     logger.warning(
#         "Connection invalidated (id: %d) due to error: %s",
#         id(dbapi_connection),
#         exception,
#     )


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with automatic cleanup."""
    session = SessionLocal()
    session_id = id(session)
    logger.debug("Created new database session (id: %d)", session_id)
    try:
        # Test the connection immediately
        await session.execute(text("SELECT 1"))
        yield session
        await session.commit()
        logger.debug("Committed database session (id: %d)", session_id)
    except Exception as e:
        logger.error(
            "Error in database session (id: %d): %s",
            session_id,
            e,
            exc_info=True,
        )
        try:
            await session.rollback()
            logger.debug("Rolled back database session (id: %d)", session_id)
        except Exception as rollback_error:
            logger.error(
                "Failed to rollback session (id: %d): %s",
                session_id,
                rollback_error,
            )
        raise
    finally:
        try:
            await session.close()
            logger.debug("Closed database session (id: %d)", session_id)
        except Exception as close_error:
            logger.error(
                "Error while closing session (id: %d): %s",
                session_id,
                close_error,
            )


async def get_session() -> AsyncSession:
    """Get a new database session.

    Note: This is kept for backward compatibility.
    New code should use get_db_session() context manager instead.
    """
    session = SessionLocal()
    session_id = id(session)
    logger.debug("Created new database session via legacy method (id: %d)", session_id)
    try:
        # Test the connection
        await session.execute(text("SELECT 1"))
        logger.debug("Successfully tested database connection (session id: %d)", session_id)
        return session
    except DBAPIError as e:
        logger.error(
            "Failed to create database session (id: %d): %s",
            session_id,
            e,
            exc_info=True,
        )
        try:
            await session.close()
            logger.debug("Closed failed database session (id: %d)", session_id)
        except Exception as close_error:
            logger.error(
                "Error while closing failed session (id: %d): %s",
                session_id,
                close_error,
            )
        raise
