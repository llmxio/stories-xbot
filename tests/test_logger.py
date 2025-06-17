import logging
import os
import shutil
import tempfile

import pytest

from config.logger import get_logger, initialize_project_logger


@pytest.fixture
def temp_log_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


def test_initialize_project_logger_stdout_stderr(monkeypatch, capsys):
    # Remove all handlers for root logger to avoid duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    initialize_project_logger("test_logger", is_stdout_debug=True)
    logger = logging.getLogger("test_logger")
    logger.info("info message")
    logger.error("error message")
    out, err = capsys.readouterr()
    assert "info message" in out
    assert "error message" in err


def test_initialize_project_logger_file_handlers(temp_log_dir):
    logger_name = "file_logger"
    initialize_project_logger(logger_name, path_dir_where_to_store_logs=temp_log_dir)
    logger = logging.getLogger(logger_name)
    logger.debug("debug file message")
    logger.error("error file message")
    logs_dir = os.path.join(temp_log_dir, "Logs")
    debug_log_path = os.path.join(logs_dir, "debug.log")
    error_log_path = os.path.join(logs_dir, "errors.log")
    # Ensure log files are created
    assert os.path.exists(debug_log_path)
    assert os.path.exists(error_log_path)
    # Check contents
    with open(debug_log_path) as f:
        contents = f.read()
        assert "debug file message" in contents
        assert "error file message" in contents
    with open(error_log_path) as f:
        contents = f.read()
        assert "error file message" in contents


def test_get_logger_initializes(monkeypatch):
    logger = get_logger("get_logger_test")
    assert isinstance(logger, logging.Logger)
    logger.info("get_logger info")
    logger.error("get_logger error")
