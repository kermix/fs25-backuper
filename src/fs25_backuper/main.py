import datetime

from fs25_backuper.config import Config
from fs25_backuper.downloader import Downloader
from fs25_backuper.uploader.fs import FileSystemUploader
from fs25_backuper.uploader.s3 import S3Uploader

if __name__ == "__main__":
    c = Config()  # type: ignore[call-arg]
    d = Downloader(c)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{c.backup_filename_prefix}_{timestamp}.zip"

    savegame_path = c.backup_path.joinpath(file_name)

    d.download_savegame(savegame_path)

    if c.s3_upload:
        s3_uploader = S3Uploader(c.s3_upload)
        s3_key = savegame_path.name
        s3_uploader.upload(savegame_path, file_name)

    if c.file_system_upload:
        fs_uploader = FileSystemUploader(c.file_system_upload)
        fs_uploader.upload(savegame_path)

    if c.ftp_upload:
        pass  # TODO: implement FTP upload
