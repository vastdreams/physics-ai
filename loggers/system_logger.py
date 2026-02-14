"""
System logging module.

Provides comprehensive logging to support debugging,
monitoring, and future AI transition.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any


class SystemLogger:
    """System-wide logger for tracking all operations.

    Provides structured logging to both file and console.
    """

    def __init__(self, log_dir: str = "logs", log_level: str = "INFO") -> None:
        """Initialize system logger.

        Args:
            log_dir: Directory for log files.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger("PhysicsAI")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        log_file = self.log_dir / f"system_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.log("SystemLogger initialized", level="INFO")

    def log(self, message: str, level: str = "INFO", **kwargs: Any) -> None:
        """Log a message.

        Args:
            message: Message to log.
            level: Log level (DEBUG, INFO, WARNING, ERROR).
            **kwargs: Additional context appended to the message.
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)

        if kwargs:
            message = f"{message} | Context: {kwargs}"

        log_method(message)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.log(message, level="DEBUG", **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.log(message, level="INFO", **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.log(message, level="WARNING", **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.log(message, level="ERROR", **kwargs)
