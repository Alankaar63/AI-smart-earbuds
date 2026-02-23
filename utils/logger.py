"""Logging helper utilities for consistent console output."""

import logging


def setup_logger(name: str = "smart_earphone", level: int = logging.INFO) -> logging.Logger:
    """Create and configure a stream logger once."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger
