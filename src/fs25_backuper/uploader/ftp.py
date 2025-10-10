import re
from datetime import datetime
from ftplib import FTP, all_errors
from pathlib import Path

from fs25_backuper.config import FTPUploadConfig
from fs25_backuper.error import CleanError, UploadError
from fs25_backuper.logger import Logger
from fs25_backuper.uploader.base import BaseUploader


class FTPUploader(BaseUploader):
    def __init__(self, config: FTPUploadConfig) -> None:
        self.logger = Logger().get_logger()

        self.__setup_client(config)

        self.path = config.directory_path

        self.create_remote_directory(self.path)

        self.number_of_backups = config.number_of_backups

        super().__init__()

    def __enter__(self) -> "FTPUploader":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        self.client.quit()

    def __setup_client(self, config: FTPUploadConfig) -> None:
        try:
            self.client = FTP()
            self.client.connect(config.host.host, config.host.port)  # type: ignore[arg-type]
            self.client.login(
                config.username.get_secret_value(), config.password.get_secret_value()
            )
        except all_errors as e:
            raise UploadError(f"FTP connection error: {str(e)}") from e

    def create_remote_directory(self, path: str) -> None:
        try:
            self.client.mkd(path)
            self.logger.info(f"Created remote directory: {path}")
        except Exception:
            pass

    def upload(self, file_path: Path) -> None:
        try:
            self.logger.debug(f"Uploading {file_path} to FTP server at {self.path}")
            with open(file_path, "rb") as file:
                self.client.storbinary(f"STOR {self.path}/{file_path.name}", file)
            self.logger.info(f"Uploaded {file_path} to FTP server at {self.path}")
            self.clean_backups()
        except Exception as e:
            self.logger.error(
                f"Failed to upload {file_path} to FTP server at {self.path}: {e}"
            )

    def _list_backups(self) -> list[tuple[str, datetime]]:
        def parse_line(line: str) -> tuple[str, datetime]:
            match = re.match(
                r"^[\-dl][\w\-]{9}\s+\d+\s+\w+\s+\w+\s+\d+\s+(\w+\s+\d+\s+[\d:]+)\s+(.+)$",
                line,
            )
            if match:
                date_str = match.group(1)
                filename = match.group(2)
                current_year = datetime.now().year
                date = datetime.strptime(f"{date_str} {current_year}", "%b %d %H:%M %Y")
                return filename, date
            raise CleanError(
                f"Unrecognized FTP line format: {line}. Only Unix-style listings are supported."
            )

        line_list: list[str] = []
        self.client.retrlines(f"LIST {self.path}", line_list.append)  # type: ignore

        if not line_list:
            return []

        backup_list = list(map(lambda x: parse_line(x), line_list))

        return backup_list

    def _remove_backup(self, backup_path: str) -> None:  # type: ignore[override]
        try:
            self.client.delete(f"{self.path}/{backup_path}")
            self.logger.info(
                f"Deleted backup: {backup_path} from FTP server at {self.path}"
            )
        except all_errors as e:
            raise CleanError(f"FTP remove error: {str(e)}") from e

    def _get_outdated_backups(self) -> list:
        backups = self._list_backups()
        if self.number_of_backups is None:
            return []
        if len(backups) <= self.number_of_backups:
            return []
        backups = sorted(backups, key=lambda x: x[1])
        return [b[0] for b in backups[: -self.number_of_backups]]
