import logging

from fs25_backuper.singleton import Singleton


class Logger(Singleton):
    def _initialize(self, level=logging.DEBUG):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        self.logger.propagate = False

        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def set_level(self, level):
        self.logger.setLevel(level)

    def get_logger(self):
        if not hasattr(self, "logger"):
            self._initialize()
        return self.logger
