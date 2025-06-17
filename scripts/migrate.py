#!/usr/bin/env python3
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def run_migrations():
    """Run database migrations."""
    # Create Alembic configuration
    alembic_cfg = Config(str(project_root / "alembic.ini"))

    # Run the migration
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run_migrations()
