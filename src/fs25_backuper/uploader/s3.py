from pathlib import Path
from typing import override

import boto3
from boto3.exceptions import Boto3Error

from fs25_backuper.config import S3UploadConfig
from fs25_backuper.error import CleanError, UploadError
from fs25_backuper.uploader.base import BaseUploader


class S3Uploader(BaseUploader):
    def __init__(self, config: S3UploadConfig) -> None:
        self.s3_client = boto3.client(
            service_name="s3",
            aws_access_key_id=config.access_key.get_secret_value(),
            aws_secret_access_key=config.secret_key.get_secret_value(),
            region_name=config.region,
        )

        self.bucket_name = config.bucket_name
        self.number_of_backups = config.number_of_backups

        super().__init__()

    def __enter__(self) -> "S3Uploader":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        self.s3_client.close()

    @override
    def upload(self, file_path: Path, s3_key: str) -> None:
        try:
            self.logger.debug(
                f"Uploading {file_path} to s3://{self.bucket_name}/{s3_key}"
            )
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            self.logger.info(
                f"Uploaded {file_path} to s3://{self.bucket_name}/{s3_key}"
            )

            self.clean_backups()
        except (Boto3Error) as e:
            raise UploadError(f"S3 upload error: {str(e)}") from e

    def _remove_backup(self, s3_key: str) -> None:  # type: ignore[override]
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            self.logger.info(f"Deleted backup: {s3_key} in buket {self.bucket_name}")
        except OSError as e:
            raise CleanError(f"File system remove error: {str(e)}") from e

    def _list_backups(self) -> list[dict]:
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            backups = response.get("Contents", [])
            return backups
        except (Boto3Error) as e:
            raise UploadError(f"S3 list error: {str(e)}") from e

    def _get_outdated_backups(self) -> list[dict]:
        backups = self._list_backups()
        if self.number_of_backups is None:
            return []
        if len(backups) <= self.number_of_backups:
            return []
        backups = sorted(backups, key=lambda x: x["LastModified"])
        return [b["Key"] for b in backups[: -self.number_of_backups]]
