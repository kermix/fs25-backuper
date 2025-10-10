# mypy: disable-error-code="call-overload, literal-required"

import tempfile
from typing import Optional, Union

from pydantic import (
    AliasChoices,
    BaseModel,
    DirectoryPath,
    Field,
    FtpUrl,
    HttpUrl,
    NewPath,
    SecretStr,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from fs25_backuper.singleton import Singleton

prefix = "FS25_BACKUPER_"

NewOrExistingPath = Union[DirectoryPath | NewPath]


class S3UploadConfig(BaseModel):
    access_key: SecretStr = Field()
    secret_key: SecretStr = Field()
    bucket_name: str = Field()
    region: str = Field()
    number_of_backups: Optional[int] = Field(None)


class FileSystemUploadConfig(BaseModel):
    directory_path: NewOrExistingPath = Field()
    number_of_backups: Optional[int] = Field(None)


class FTPUploadConfig(BaseModel):
    host: FtpUrl = Field()
    username: SecretStr = Field()
    password: SecretStr = Field()
    directory_path: str = Field(default=".")
    number_of_backups: Optional[int] = Field(None)

    @field_validator("host", mode="after")
    def validate_host(cls, v: FtpUrl) -> FtpUrl:
        if v.host is None:
            raise ValueError("FTP host must be specified.")
        return v


class Config(BaseSettings, Singleton):
    login: SecretStr = Field(alias=AliasChoices(f"{prefix}LOGIN", "login"))
    password: SecretStr = Field(alias=AliasChoices(f"{prefix}PASSWORD", "password"))
    url: HttpUrl = Field(alias=AliasChoices(f"{prefix}URL", "url"))
    savegame: str = Field(
        default="savegame1", alias=AliasChoices(f"{prefix}SAVEGAME", "savegame")
    )
    backup_path: NewOrExistingPath = Field(
        default=tempfile.gettempdir(),
        alias=AliasChoices(f"{prefix}DOWNLOAD_PATH", "download_path"),
    )
    backup_filename_prefix: str = Field(
        default="savegame_backup",
        alias=AliasChoices(f"{prefix}BACKUP_FILENAME_PREFIX", "backup_filename_prefix"),
    )
    log_level: str = Field(
        default="DEBUG", alias=AliasChoices(f"{prefix}LOG_LEVEL", "log_level")
    )
    s3_upload: Optional[S3UploadConfig] = Field(
        default=None, alias=f"{prefix}S3_UPLOAD"
    )

    file_system_upload: Optional[FileSystemUploadConfig] = Field(
        default=None, alias=f"{prefix}FILE_SYSTEM_UPLOAD"
    )

    ftp_upload: Optional[FTPUploadConfig] = Field(
        default=None, alias=f"{prefix}FTP_UPLOAD"
    )

    model_config = SettingsConfigDict(
        # cli_parse_args=True,
        env_prefix=prefix,
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    cleanup_downloaded_savegame: bool = Field(
        default=True,
        description="Whether to delete the downloaded savegame after upload.",
    )
