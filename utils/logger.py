"""
=========================================================
PLATFORM LOGGER
=========================================================

Purpose:
Centralized logging configuration for the
Institutional Quant Platform.

=========================================================
"""

from __future__ import annotations

import logging

from config.paths import (
    LOG_DIR,
)
from config.settings import (
    ENABLE_CONSOLE_LOGGING,
    ENABLE_FILE_LOGGING,
    LOG_LEVEL,
)

LOG_FILE = LOG_DIR / "platform.log"


def get_logger(
    name: str,
) -> logging.Logger:
    """
    Return a configured logger.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(
        getattr(
            logging,
            LOG_LEVEL.upper(),
        )
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    if ENABLE_CONSOLE_LOGGING:
        console = logging.StreamHandler()

        console.setFormatter(formatter)

        logger.addHandler(console)

    if ENABLE_FILE_LOGGING:
        LOG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_handler = logging.FileHandler(
            LOG_FILE,
            encoding="utf-8",
        )

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    logger.propagate = False

    return logger
