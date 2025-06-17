#!/usr/bin/env python3
import logging
import sys
from pathlib import Path

# Add the project root to the Python path before any other imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from alembic import command  # type: ignore
from alembic.config import Config  # type: ignore

# Use the project logger if available, otherwise fallback to basicConfig
try:
    from config.logger import get_logger

    LOGGER = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    LOGGER = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations."""
    LOGGER.info("Running migrations...")
    # Create Alembic configuration
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    LOGGER.info("Alembic configuration loaded from: %s", alembic_cfg.config_file_name)
    # Run the migration
    command.upgrade(alembic_cfg, "head")
    LOGGER.info("Migrations completed successfully")


if __name__ == "__main__":
    run_migrations()
