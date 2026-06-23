import logging
import sys
from pathlib import Path

import yaml

_LOG_FORMAT = "[%(asctime)s] [%(program)s] [%(levelname)s] %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _load_log_config() -> tuple[str, str]:
    config_path = Path(__file__).parent / "config.yaml"
    try:
        with open(config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg["logs"]["file"], cfg["logs"]["level"]
    except Exception:
        return "app.log", "INFO"


def get_logger(program_name: str) -> logging.Logger:
    log_file, level_str = _load_log_config()
    level = getattr(logging, level_str.upper(), logging.INFO)

    logger = logging.getLogger(program_name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.program = program_name
        return record

    logging.setLogRecordFactory(record_factory)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    file_handler = logging.FileHandler(
        Path(__file__).parent / log_file, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
