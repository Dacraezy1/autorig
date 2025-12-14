import logging
import os
from pathlib import Path

def setup_logging():
    log_dir = Path(os.path.expanduser("~/.autorig/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "autorig.log"

    logger = logging.getLogger("autorig")
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    logger.addHandler(fh)
    return logger