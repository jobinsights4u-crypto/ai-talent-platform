"""
utils/logger.py
---------------
Centralised logging factory for the AI Talent Intelligence Platform.
"""

from __future__ import annotations

import logging
import sys

from config import LOG_FORMAT, LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger configured with the platform's format.

    Parameters
    ----------
    name : str
        Usually ``__name__`` of the calling module.

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    return logger
