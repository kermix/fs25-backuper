import logging
from enum import Enum

from fs25_backuper.singleton import Singleton


class LogLevel(Enum):
    CRITICAL = logging.CRITICAL
    FATAL = CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


class Logger(Singleton):
    def _initialize(self, level: LogLevel) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level.value)
        self.logger.propagate = False

        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def set_level(self, level: int) -> None:
        self.logger.setLevel(level)

    def get_logger(self, level: LogLevel = LogLevel.DEBUG) -> logging.Logger:
        if not hasattr(self, "logger"):
            self._initialize(level)
        return self.logger
