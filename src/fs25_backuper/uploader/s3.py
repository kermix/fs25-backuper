from functools import cache

import boto3

from boto3.exceptions import Boto3Error

from fs25_backuper.logger import Logger
from fs25_backuper.error import UploadError

class S3Uploader:
    def __init__(self, config):        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            region_name=config.region
        )
        
        self.bucket_name = config.bucket_name
        self.number_of_backups = config.number_of_backups
        
        self.logger = Logger().get_logger()
        
    
    def upload(self, file_path: str, s3_key: str):
        try:
            self.logger.debug(f"Uploading {file_path} to s3://{self.bucket_name}/{s3_key}")
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            self.logger.info(f"Uploaded {file_path} to s3://{self.bucket_name}/{s3_key}")
            
            outdated_backups = self._get_outdated_backups()
            for backup in outdated_backups:
                self.logger.info(f"Deleting outdated backup: {backup['Key']}")
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=backup['Key'])
        except (Boto3Error) as e:
            raise UploadError(f"S3 upload error: {str(e)}") from e
    
    @cache   
    def _list_backups(self):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            backups = response.get('Contents', [])
            return backups
        except (Boto3Error) as e    :
            raise UploadError(f"S3 list error: {str(e)}") from e
    
    def _get_outdated_backups(self):
        backups = self._list_backups()
        if self.number_of_backups is None:
            return []
        if len(backups) <= self.number_of_backups:
            return []
        backups = sorted(backups, key=lambda x: x['LastModified'])
        return backups[:-self.number_of_backups]
    
    