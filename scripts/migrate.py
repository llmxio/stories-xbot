#!/usr/bin/env python3
import logging
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config

# from config.logger import get_logger

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

print(project_root)

LOGGER = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations."""
    LOGGER.info("Running migrations...")
    # Create Alembic configuration
    alembic_cfg = Config(project_root / "alembic.ini")

    LOGGER.info("Alembic configuration: %s", alembic_cfg)

    LOGGER.info("Running migrations...")

    # Run the migration
    command.upgrade(alembic_cfg, "head")

    LOGGER.info("Migrations completed successfully")


if __name__ == "__main__":
    run_migrations()
