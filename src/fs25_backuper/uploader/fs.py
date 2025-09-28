import os
import shutil
from pathlib import Path

from fs25_backuper.config import FileSystemUploadConfig
from fs25_backuper.error import UploadError
from fs25_backuper.logger import Logger


class FileSystemUploader:
    def __init__(self, config: FileSystemUploadConfig):
        self.directory_path = Path(config.directory_path)
        self.number_of_backups = config.number_of_backups

        self.logger = Logger().get_logger()

        if not self.directory_path.exists():
            self.directory_path.mkdir(parents=True, exist_ok=True)

    def upload(self, file_path: Path) -> None:
        try:
            self.logger.debug(f"Copying {file_path} to {self.directory_path}")
            destination = self.directory_path / file_path.name
            shutil.copy2(file_path, destination)
            self.logger.info(f"File {file_path} copied to {destination}")

            for backup in self._get_outdated_backups():
                self.logger.info(f"Deleting outdated backup: {backup}")
                os.remove(backup)
        except Exception as e:
            raise UploadError(f"File system upload error: {str(e)}") from e

    def _list_backups(self) -> list[Path]:
        return list(self.directory_path.glob("*.zip"))

    def _get_outdated_backups(self) -> list[Path]:
        backups = self._list_backups()
        if self.number_of_backups is None:
            return []
        if len(backups) <= self.number_of_backups:
            return []
        backups = sorted(backups, key=os.path.getmtime)
        return backups[: -self.number_of_backups]
