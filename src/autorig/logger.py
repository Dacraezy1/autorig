import logging
import os
from pathlib import Path
from datetime import datetime


def setup_logging(verbose: bool = False):
    log_dir = Path(os.path.expanduser("~/.autorig/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create a log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"autorig_{timestamp}.log"

    logger = logging.getLogger("autorig")
    logger.setLevel(logging.DEBUG)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler with detailed formatting
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    fh.setFormatter(file_formatter)

    # Console handler for verbose mode
    if verbose:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        ch.setFormatter(console_formatter)
        logger.addHandler(ch)

    logger.addHandler(fh)
    return logger
