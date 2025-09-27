from typing import Optional
import tempfile

from pydantic import BaseModel, HttpUrl, Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

from fs25_backuper.singleton import Singleton

prefix = "FS25_BACKUPER_"

class S3UploadConfig(BaseModel):
    access_key: str = Field()
    secret_key: str = Field()
    bucket_name: str = Field()
    region: str = Field()
    number_of_backups: Optional[int] = Field(
        None
    )
      
                                            
class Config(BaseSettings, Singleton):
    username: str = Field(alias=AliasChoices(f"{prefix}USERNAME", "username"))
    password: str = Field(alias=AliasChoices(f"{prefix}PASSWORD", "password"))
    url: HttpUrl = Field(alias=AliasChoices(f"{prefix}URL", "url"))
    savegame: str = Field(
        default="savegame1", alias=AliasChoices(f"{prefix}SAVEGAME", "savegame")
    )
    backup_path: str = Field(
        default=tempfile.gettempdir(),
        alias=AliasChoices(f"{prefix}DOWNLOAD_PATH", "download_path"),
    )
    backup_filename_prefix: str = Field(
        default="savegame_backup", alias=AliasChoices(f"{prefix}BACKUP_FILENAME_PREFIX", "backup_filename_prefix")
    )
    log_level: str = Field(
        default="DEBUG", alias=AliasChoices(f"{prefix}LOG_LEVEL", "log_level")
    )
    s3_upload: Optional[S3UploadConfig] = Field(default=None, alias=f"{prefix}S3_UPLOAD")
    

    model_config = SettingsConfigDict(
        # cli_parse_args=True,
        env_prefix=prefix,
        env_nested_delimiter = '__'
    )
