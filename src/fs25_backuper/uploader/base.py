from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Union

from fs25_backuper.error import CleanError
from fs25_backuper.logger import Logger


class BaseUploader(ABC):
    """Base class for uploaders"""

    def __init__(self):
        self.logger = Logger().get_logger()

    @abstractmethod
    def upload(self, file_path: Path, *args, **kwargs) -> None:
        raise NotImplementedError

    def clean_backups(self) -> None:
        self.logger.debug("Starting cleanup of old backups")
        try:
            outdated_backups = self._get_outdated_backups()
            if outdated_backups:
                for backup in outdated_backups:
                    self.logger.debug(f"Deleting outdated backup: {backup}")
                    self._remove_backup(backup)
            else:
                self.logger.info("No outdated backups to delete")
            self.logger.debug("Cleanup of old backups completed")
        except OSError as e:
            raise CleanError(f"File system cleanup error: {str(e)}") from e

    @abstractmethod
    def _remove_backup(self, backup_path: Union[Path | str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def _list_backups(self) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    def _get_outdated_backups(self) -> list[Any]:
        raise NotImplementedError
