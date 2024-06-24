import logging
from datetime import datetime
from pathlib import Path

from rich.logging import RichHandler

from data_safe_haven.logging.logger import (
    PlainFileHandler,
    from_ansi,
    get_logger,
    logfile_name,
    set_console_level,
    show_console_level,
)


class TestFromAnsi:
    def test_from_ansi(self, capsys):
        logger = get_logger()
        from_ansi(logger, "\033[31;1;4mHello\033[0m")
        out, _ = capsys.readouterr()
        assert "Hello" in out
        assert r"\033" not in out


class TestLogFileName:
    def test_logfile_name(self):
        name = logfile_name()
        assert name.endswith(".log")
        date = name.split(".")[0]
        assert datetime.strptime(date, "%Y-%m-%d")  # noqa: DTZ007


class TestGetLogger:
    def test_get_logger(self):
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "data_safe_haven"
        assert hasattr(logger, "console_handler")
        assert hasattr(logger, "file_handler")


class TestLogger:
    def test_constructor(self, log_directory):
        logger = get_logger()

        assert isinstance(logger.file_handler, PlainFileHandler)
        assert isinstance(logger.console_handler, RichHandler)

        assert logger.file_handler.baseFilename == f"{log_directory}/test.log"
        log_file = Path(logger.file_handler.baseFilename)
        logger.info("hello")
        assert log_file.is_file()


class TestSetConsoleLevel:
    def test_set_console_level(self):
        logger = get_logger()
        assert logger.console_handler.level == logging.INFO
        set_console_level(logging.DEBUG)
        assert logger.console_handler.level == logging.DEBUG

    def test_set_console_level_stdout(self, capsys):
        logger = get_logger()
        set_console_level(logging.DEBUG)
        logger.debug("hello")
        out, _ = capsys.readouterr()
        assert "hello" in out


class TestShowConsoleLevel:
    def test_show_console_level(self):
        logger = get_logger()
        assert not logger.console_handler._log_render.show_level
        show_console_level()
        assert logger.console_handler._log_render.show_level

    def test_show_console_level_stdout(self, capsys):
        logger = get_logger()
        show_console_level()
        logger.info("hello")
        out, _ = capsys.readouterr()
        assert "INFO" in out
