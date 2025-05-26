"""
Logging configuration.
"""

import logging

from config.settings import LOG_FORMAT, LOG_LEVEL


def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with the specified name.

    Args:
        name: Name of the logger

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

    return logger
