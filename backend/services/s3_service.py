"""
S3 File Upload Service

Handles uploading files to AWS S3 bucket for product images and other assets.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import UploadFile
from typing import Optional
import logging
import uuid
import os
from core.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    """Service for handling S3 file operations"""
    
    def __init__(self):
        """Initialize S3 client with credentials from settings"""
        self.s3_client = None
        self.bucket_name = settings.S3_BUCKET_NAME
        
        # Initialize S3 client if credentials are available
        if all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_REGION]):
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                self.s3_client = None
        else:
            logger.warning("S3 credentials not configured")
    
    def is_configured(self) -> bool:
        """Check if S3 is properly configured"""
        return self.s3_client is not None and self.bucket_name is not None
    
    def validate_image_file(self, file: UploadFile) -> bool:
        """
        Validate uploaded file is an allowed image type and size
        
        Args:
            file: The uploaded file
            
        Returns:
            True if file is valid, False otherwise
        """
        # Check file extension
        if not file.filename:
            return False
            
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in settings.allowed_extensions_list:
            logger.warning(f"Invalid file extension: {file_extension}")
            return False
        
        # Check file size (FastAPI's UploadFile doesn't have size readily available)
        # We'll check this during upload instead
        
        return True
    
    async def upload_product_image(self, file: UploadFile, product_name: str = None) -> Optional[str]:
        """
        Upload product image to S3 bucket
        
        Args:
            file: The uploaded image file
            product_name: Optional product name for organizing files
            
        Returns:
            S3 object key (filename) if successful, None if failed
        """
        if not self.is_configured():
            logger.error("S3 not configured, cannot upload file")
            return None
        
        if not self.validate_image_file(file):
            logger.error("Invalid image file")
            return None
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Check file size
            if len(file_content) > settings.MAX_UPLOAD_SIZE:
                logger.error(f"File too large: {len(file_content)} bytes (max: {settings.MAX_UPLOAD_SIZE})")
                return None
            
            # Generate unique filename while preserving original extension
            file_extension = file.filename.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Create S3 key (path in bucket)
            s3_key = f"images/{unique_filename}"
            
            # Determine content type
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            
            content_type = file.content_type or content_type_map.get(file_extension, f"image/{file_extension}")
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    'original_filename': file.filename,
                    'product_name': product_name or 'unknown',
                    'uploaded_by': 'admin'  # Could be dynamic based on user
                }
            )
            
            logger.info(f"Successfully uploaded {file.filename} as {s3_key}")
            
            # Return only the filename (without folder prefix) to store in database
            return unique_filename
            
        except ClientError as e:
            logger.error(f"AWS S3 error uploading file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            return None
        finally:
            # Reset file pointer for potential reuse
            await file.seek(0)
    
    def delete_product_image(self, s3_key: str) -> bool:
        """
        Delete product image from S3 bucket
        
        Args:
            s3_key: The filename (without folder prefix) stored in database
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            logger.error("S3 not configured, cannot delete file")
            return False
        
        if not s3_key:
            return True  # Nothing to delete
        
        try:
            # Add images/ prefix if not already present
            full_s3_key = s3_key if s3_key.startswith('images/') else f"images/{s3_key}"
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=full_s3_key
            )
            logger.info(f"Successfully deleted S3 object: {full_s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"AWS S3 error deleting file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False
    
    def get_image_url(self, s3_key: str) -> Optional[str]:
        """
        Get public URL for S3 object
        
        Args:
            s3_key: The filename (without folder prefix) stored in database
            
        Returns:
            Public URL if accessible, None otherwise
        """
        if not self.is_configured() or not s3_key:
            return None
        
        try:
            # Add images/ prefix if not already present
            full_s3_key = s3_key if s3_key.startswith('images/') else f"images/{s3_key}"
            
            # Generate public URL (assumes bucket is configured for public read)
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{full_s3_key}"
            return url
        except Exception as e:
            logger.error(f"Error generating S3 URL: {e}")
            return None
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for private S3 object access
        
        Args:
            s3_key: The filename (without folder prefix) stored in database
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL if successful, None otherwise
        """
        if not self.is_configured() or not s3_key:
            return None
        
        try:
            # Add images/ prefix if not already present
            full_s3_key = s3_key if s3_key.startswith('images/') else f"images/{s3_key}"
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': full_s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None


# Create global S3 service instance
s3_service = S3Service()