#!/usr/bin/env python3
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from config import get_logger

# Add the project root to the Python path before any other imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

LOG = get_logger(__name__)


def run_migrations():
    """Run database migrations."""
    LOG.info("Running migrations...")
    # Create Alembic configuration
    alembic_cfg = Config("pyproject.toml")
    LOG.info("Alembic configuration loaded from: %s", alembic_cfg.config_file_name)
    # Run the migration
    command.upgrade(alembic_cfg, "head")
    LOG.info("Migrations completed successfully")


if __name__ == "__main__":
    run_migrations()
