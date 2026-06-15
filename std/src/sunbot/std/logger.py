import logging
from logging import Logger

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(*, level: int = logging.INFO) -> None:
    """Canonical one-call logging setup for the platform.

    Apply once at process start so every component logs the same way.
    """
    logging.basicConfig(level=level, format=_LOG_FORMAT)


def get_logger(name: str) -> Logger:
    return logging.getLogger(name)
