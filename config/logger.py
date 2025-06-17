import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional


def initialize_project_logger(
    name: Optional[str] = None,
    path_dir_where_to_store_logs: str = "logs",
    is_stdout_debug: bool = True,
    is_to_propagate_to_root_logger: bool = True,
):
    """
    Initialize a project logger with optional file logging and custom settings.
    Usage:
        from .logger import initialize_project_logger
        initialize_project_logger(__name__)
        LOGGER = logging.getLogger(__name__)
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = is_to_propagate_to_root_logger

    # Remove all handlers associated with the logger object
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler for stdout (INFO, WARNING)
    class InfoFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno in (logging.INFO, logging.WARNING)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO if not is_stdout_debug else logging.DEBUG)
    stdout_handler.addFilter(InfoFilter())
    stdout_format = logging.Formatter("%(message)s")
    stdout_handler.setFormatter(stdout_format)
    logger.addHandler(stdout_handler)

    # Console handler for stderr (ERROR, CRITICAL)
    class ErrorFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno in (logging.ERROR, logging.CRITICAL)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.addFilter(ErrorFilter())
    stderr_format = logging.Formatter(
        "[%(levelname)s]: %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    stderr_handler.setFormatter(stderr_format)
    logger.addHandler(stderr_handler)

    # Optionally add file handlers
    if path_dir_where_to_store_logs:
        logs_dir = os.path.join(path_dir_where_to_store_logs, "Logs")
        os.makedirs(logs_dir, exist_ok=True)
        debug_log_path = os.path.join(logs_dir, "debug.log")
        error_log_path = os.path.join(logs_dir, "errors.log")

        debug_file_handler = RotatingFileHandler(
            debug_log_path, maxBytes=10 * 1024 * 1024, backupCount=1
        )
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        logger.addHandler(debug_file_handler)

        error_file_handler = RotatingFileHandler(
            error_log_path, maxBytes=10 * 1024 * 1024, backupCount=1
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        logger.addHandler(error_file_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    initialize_project_logger(name)
    return logging.getLogger(name)
