# loggers/
"""
System logging module.

First Principle Analysis:
- Logging is essential for debugging, monitoring, and AI transition
- Must support multiple log levels and outputs
- Mathematical foundation: information theory for log compression
- Architecture: modular logger with multiple handlers

Planning:
1. Implement multi-level logging
2. Create file and console handlers
3. Add structured logging support
4. Design for AI-readable logs
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class SystemLogger:
    """
    System-wide logger for tracking all operations.
    
    Provides comprehensive logging to support debugging,
    monitoring, and future AI transition.
    """
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        Initialize system logger.
        
        Args:
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger("PhysicsAI")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        log_file = self.log_dir / f"system_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self.log("SystemLogger initialized", level="INFO")
    
    def log(self, message: str, level: str = "INFO", **kwargs: Any) -> None:
        """
        Log a message.
        
        Args:
            message: Message to log
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            **kwargs: Additional context
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

