#!/usr/bin/env python3

import datetime

from fs25_backuper.config import Config
from fs25_backuper.downloader import Downloader
from fs25_backuper.logger import Logger
from fs25_backuper.uploader.fs import FileSystemUploader
from fs25_backuper.uploader.ftp import FTPUploader
from fs25_backuper.uploader.s3 import S3Uploader


def run():
    c = Config()  # type: ignore[call-arg]

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{c.backup_filename_prefix}_{timestamp}.zip"

    savegame_path = c.backup_path.joinpath(file_name)

    logger = Logger().get_logger(c.log_level)

    with Downloader(c) as d:
        d.download_savegame(savegame_path)

        if c.s3_upload:
            logger.debug("Starting S3 upload")
            with S3Uploader(c.s3_upload) as s3_uploader:
                s3_uploader.upload(savegame_path, file_name)

        if c.file_system_upload:
            logger.debug("Starting file system upload")
            with FileSystemUploader(c.file_system_upload) as fs_uploader:
                fs_uploader.upload(savegame_path)

        if c.ftp_upload:
            logger.debug("Starting FTP upload")
            with FTPUploader(c.ftp_upload) as ftp_uploader:
                ftp_uploader.upload(savegame_path)


if __name__ == "__main__":
    run()
