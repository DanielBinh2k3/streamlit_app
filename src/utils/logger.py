import functools
import json
import logging
import os
import traceback
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

console = Console()

os.makedirs("logs", exist_ok=True)


class CustomJsonFormatter(logging.Formatter):
    """Custom JSON formatter for logging that doesn't require pythonjsonlogger."""

    def format(self, record):
        log_record = {
            "asctime": self.formatTime(record),
            "levelname": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if available
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        # Add extra fields if available
        if hasattr(record, "extra") and record.extra:
            log_record.update(record.extra)

        return json.dumps(log_record)


class Logger:
    _instances = {}

    def __new__(cls, name: str = "default"):
        if name not in cls._instances:
            cls._instances[name] = super().__new__(cls)
            cls._instances[name]._setup_logger(name)
        return cls._instances[name]

    def _setup_logger(self, name: str):
        self.logger = logging.getLogger(f"erpbot-{name}")
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers if any
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Custom JSON formatter for file logging
        json_formatter = CustomJsonFormatter()

        # Rich handler for console output
        rich_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            show_time=True,
            omit_repeated_times=False,
            show_level=True,
        )
        rich_handler.setLevel(logging.INFO)
        self.logger.addHandler(rich_handler)

        # File handler with JSON formatting
        file_handler = logging.FileHandler(
            f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(json_formatter)
        self.logger.addHandler(file_handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def info(self, message, extra=None):
        self.logger.info(message, extra=extra)

    def error(self, message, exc_info=None, extra=None):
        self.logger.error(message, exc_info=exc_info, extra=extra)

    def warning(self, message, extra=None):
        self.logger.warning(message, extra=extra)

    def debug(self, message, extra=None):
        self.logger.debug(message, extra=extra)


def auto_log_error(logger_name: str = "default", response_if_error: Any = None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = Logger(logger_name)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get stack trace info
                tb = traceback.extract_tb(e.__traceback__)
                frame = tb[-1]  # Last frame in traceback

                logger.error(
                    "Unexpected error",
                    extra={
                        "error": str(e),
                        "location": f"{func.__qualname__}",
                        "file": frame.filename,
                        "line": frame.lineno,
                        "function": frame.name,
                    },
                )

                if response_if_error:
                    return response_if_error
                else:
                    raise

        return wrapper

    return decorator
