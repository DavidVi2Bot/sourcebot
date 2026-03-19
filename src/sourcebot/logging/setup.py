import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level=logging.INFO, log_dir="runs/logs"):
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    log_file = Path(log_dir) / "sourcebot.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(level)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    # Third party
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)