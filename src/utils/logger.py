"""
SQUAD-CSHARP - Logger
Configuration du système de logging.
"""

import logging
import sys
from pathlib import Path

from src.utils.config import LOG_LEVEL, LOG_FILE, LOG_DIR


def setup_logger(name: str = "squad-csharp") -> logging.Logger:
    """Configure et retourne un logger pour l'application."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Impossible de créer le fichier de log : {e}")

    return logger


# Logger par défaut
logger = setup_logger()
