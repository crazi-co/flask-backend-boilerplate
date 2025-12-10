"""Logging configuration utility."""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    file_path: Optional[str] = None,
    format_string: Optional[str] = None,
    service_name: Optional[str] = None
) -> None:
    """Setup centralized logging configuration."""

    if format_string is None:
        format_string = "%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s"

    # Create handlers list
    handlers = [logging.StreamHandler(sys.stdout)]

    # Add file handler if file_path is provided
    if file_path:
        handlers.append(logging.FileHandler(file_path))

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=handlers,
        force=True  # Override any existing configuration
    )

    # Set specific loggers to avoid too verbose output
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    if service_name:
        logger = logging.getLogger(service_name)
        logger.info("Logging initialized for service: %s", service_name)


def get_logger(service_name: str) -> logging.Logger:
    """Get a logger for a specific service."""
    return logging.getLogger(f"app.services.{service_name}")
