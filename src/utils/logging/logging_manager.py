"""Centralized logging configuration for the project."""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional

# Constants
DEFAULT_LOG_DIR = "logs"
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    max_bytes: int = MAX_BYTES,
    backup_count: int = BACKUP_COUNT,
) -> logging.Logger:
    """Configure a logger with consistent formatting and rotation.

    Args:
        name: Logger name (typically __name__)
        log_file: Optional specific log file path
        level: Logging level
        max_bytes: Max size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create logs directory if needed
    os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)

    # Default log file name based on module name if not specified
    if log_file is None:
        log_file = os.path.join(DEFAULT_LOG_DIR, f"{name.split('.')[-1]}.log")

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def setup_health_logger() -> logging.Logger:
    """Configure specialized logger for health checks."""
    return setup_logger(
        "health_check", os.path.join(DEFAULT_LOG_DIR, "health.log"), level=logging.INFO
    )


def setup_audit_logger() -> logging.Logger:
    """Configure specialized logger for audit events."""
    return setup_logger("audit", os.path.join(DEFAULT_LOG_DIR, "audit.log"), level=logging.INFO)


def get_timestamp() -> str:
    """Get current timestamp in standard format.

    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(DEFAULT_DATE_FORMAT)


# Default logger for general use
default_logger = setup_logger("bar_directory_recon")
