"""
S3 Repository
"""
from typing import Optional
import boto3
from botocore.exceptions import ClientError

from app.config import settings
from app.core.logging import logger


class S3Repository:
    """
    Repository for S3 operations
    """
    
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
    
    async def upload_file(
        self,
        file_content: bytes,
        bucket: str,
        key: str,
        content_type: Optional[str] = None
    ) -> str:
        """Upload file to S3"""
        try:
            params = {
                'Bucket': bucket,
                'Key': key,
                'Body': file_content
            }
            
            if content_type:
                params['ContentType'] = content_type
            
            self.s3_client.put_object(**params)
            
            return f"s3://{bucket}/{key}"
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise
    
    async def download_file(self, bucket: str, key: str) -> bytes:
        """Download file from S3"""
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"S3 download error: {e}")
            raise
    
    async def delete_file(self, bucket: str, key: str) -> None:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
        except ClientError as e:
            logger.error(f"S3 delete error: {e}")
            raise
    
    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600
    ) -> str:
        """Generate presigned URL for file access"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"S3 presigned URL error: {e}")
            raise
