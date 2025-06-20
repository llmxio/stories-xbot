import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from config import get_config

config = get_config()


def initialize_project_logger(
    name: Optional[str] = None,
    path_dir_where_to_store_logs: str = "logs",
    is_to_propagate_to_root_logger: bool = False,
    log_level: str = "INFO",
):
    """
    Initialize a project logger with optional file logging and custom settings.
    Usage:
        from .logger import initialize_project_logger
        initialize_project_logger(__name__)
        LOGGER = logging.getLogger(__name__)
    """

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), log_level))
    logger.propagate = is_to_propagate_to_root_logger

    # Remove all handlers associated with the logger object
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Common formatter for all handlers
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler for stdout (DEBUG, INFO, WARNING)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # Console handler for stderr (ERROR, CRITICAL)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # Optionally add file handlers
    if path_dir_where_to_store_logs:
        os.makedirs(path_dir_where_to_store_logs, exist_ok=True)

        debug_log_path = os.path.join(path_dir_where_to_store_logs, "debug.log")
        error_log_path = os.path.join(path_dir_where_to_store_logs, "errors.log")

        debug_file_handler = RotatingFileHandler(debug_log_path, maxBytes=10 * 1024 * 1024, backupCount=1)
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(formatter)
        logger.addHandler(debug_file_handler)

        error_file_handler = RotatingFileHandler(error_log_path, maxBytes=10 * 1024 * 1024, backupCount=1)
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        logger.addHandler(error_file_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    initialize_project_logger(name, log_level=get_config().LOG_LEVEL)
    return logging.getLogger(name)
