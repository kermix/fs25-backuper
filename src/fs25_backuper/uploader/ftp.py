from fs25_backuper.config import FTPUploadConfig
from fs25_backuper.logger import Logger


class FTPUploader:
    def __init__(self, config: FTPUploadConfig) -> None:
        self.config = config
        self.logger = Logger().get_logger()

        raise NotImplementedError("FTPUploader is not yet implemented.")
