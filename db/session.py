"""Database session management."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, DisconnectionError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from config.config import get_config
from config.logger import get_logger

logger = get_logger(__name__)

# Get database URL from config
config = get_config()

# Configure the engine with connection pooling and retry settings
engine = create_engine(
    config.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Maximum number of connections in the pool
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,  # Timeout for getting a connection from the pool
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
    # Add retry settings
    pool_reset_on_return="rollback",  # Reset connection state on return to pool
    echo_pool=True,  # Log pool events
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@event.listens_for(Engine, "connect")
def connect(dbapi_connection, connection_record):
    """Set up connection-level configuration."""
    logger.debug(
        "New database connection established (id: %d)",
        id(dbapi_connection),
    )
    # For psycopg2, we need to handle connection setup differently
    if hasattr(dbapi_connection, "set_session"):
        # Ensure we're in a clean state
        dbapi_connection.set_session(readonly=False, autocommit=False)


@event.listens_for(Engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    """Perform health check on connection checkout."""
    logger.debug(
        "Checking out database connection (id: %d)",
        id(dbapi_connection),
    )
    try:
        # For psycopg2, execute a simple query to test the connection
        cursor = dbapi_connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
    except Exception as e:
        logger.warning(
            "Connection health check failed (id: %d): %s",
            id(dbapi_connection),
            e,
        )
        connection_record.invalidate(e)
        raise DisconnectionError() from e


@event.listens_for(Engine, "checkin")
def checkin(dbapi_connection, connection_record):
    """Log when a connection is checked back into the pool."""
    logger.debug(
        "Connection returned to pool (id: %d)",
        id(dbapi_connection),
    )


@event.listens_for(Engine, "reset")
def reset(dbapi_connection, connection_record):
    """Reset connection state."""
    logger.debug(
        "Connection reset (id: %d)",
        id(dbapi_connection),
    )
    # For psycopg2, ensure we reset the connection state
    if hasattr(dbapi_connection, "set_session"):
        dbapi_connection.set_session(readonly=False, autocommit=False)


@event.listens_for(Engine, "invalidate")
def invalidate(dbapi_connection, connection_record, exception):
    """Log when a connection is invalidated."""
    logger.warning(
        "Connection invalidated (id: %d) due to error: %s",
        id(dbapi_connection),
        exception,
    )


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get a database session with automatic cleanup."""
    session = SessionLocal()
    session_id = id(session)
    logger.debug("Created new database session (id: %d)", session_id)
    try:
        # Test the connection immediately
        session.execute(text("SELECT 1"))
        yield session
        session.commit()
        logger.debug("Committed database session (id: %d)", session_id)
    except Exception as e:
        logger.error(
            "Error in database session (id: %d): %s",
            session_id,
            e,
            exc_info=True,
        )
        try:
            session.rollback()
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
            session.close()
            logger.debug("Closed database session (id: %d)", session_id)
        except Exception as close_error:
            logger.error(
                "Error while closing session (id: %d): %s",
                session_id,
                close_error,
            )


def get_session() -> Session:
    """Get a new database session.

    Note: This is kept for backward compatibility.
    New code should use get_db_session() context manager instead.
    """
    session = SessionLocal()
    session_id = id(session)
    logger.debug("Created new database session via legacy method (id: %d)", session_id)
    try:
        # Test the connection
        session.execute(text("SELECT 1"))
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
            session.close()
            logger.debug("Closed failed database session (id: %d)", session_id)
        except Exception as close_error:
            logger.error(
                "Error while closing failed session (id: %d): %s",
                session_id,
                close_error,
            )
        raise
