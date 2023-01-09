'''
Author: Aiden Li
Date: 2023-01-09 13:47:46
LastEditors: Aiden Li (i@aidenli.net)
LastEditTime: 2023-01-09 15:27:57
Description: S3 API
'''

import boto3
import os
import logging


class S3Uploader:
    def __init__(self, target_bucket, default_remote_dir, aws_access_key_id, aws_secret_access_key, base_url=None, endpoint_url=None):
        self.target_bucket = target_bucket
        self.default_remote_dir = default_remote_dir
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.base_url = base_url
        
    def upload(self, local_path, remote_path=None):
        if not os.path.isfile(local_path):
            logging.error(f'File {local_path} is not a valid file.')
        if remote_path is None:
            remote_path = os.path.join(self.default_remote_dir, os.path.basename(local_path))
            
        try:
            s3 = boto3.resource('s3', endpoint_url=self.endpoint_url, aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
            s3.Object(self.target_bucket, remote_path).upload_file(local_path)
            
            if self.base_url is None:
                location = boto3.client('s3').get_bucket_location(Bucket=self.target_bucket)['LocationConstraint']
                base_url = f"https://s3-{location}.amazonaws.com/{self.target_bucket}"
            else:
                base_url = self.base_url if self.base_url[-1] != '/' else self.base_url[:-1]
                
            object_url = f"{base_url}/{remote_path}"
                
        except Exception as ex:
            logging.error(f'Failed to upload {local_path} to {remote_path} in bucket {self.target_bucket}. Error:\n {ex}')
            
        return object_url