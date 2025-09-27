import datetime
import os 

from fs25_backuper.config import Config
from fs25_backuper.downloader import Downloader
from fs25_backuper.uploader.s3 import S3Uploader

if __name__ == "__main__":    
    c = Config()
    d = Downloader(c)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{c.backup_filename_prefix}_{timestamp}.zip"

    savegame_path = os.path.join(c.backup_path, file_name)
        
    d.download_savegame(savegame_path)
    
    if c.s3_upload:
        uploader = S3Uploader(c.s3_upload)
        s3_key = os.path.basename(savegame_path)
        uploader.upload(savegame_path, file_name)
    