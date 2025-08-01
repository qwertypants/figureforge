"""
S3 utilities for image storage and CloudFront signed URLs
Handles uploading images and generating secure access URLs
"""

import boto3
import uuid
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from django.conf import settings
from botocore.exceptions import ClientError
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64


class S3Client:
    """Wrapper for S3 operations"""
    
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
    
    def generate_image_key(self, user_id: str, image_id: str, extension: str = 'png') -> str:
        """Generate S3 key for an image"""
        return f"images/{user_id}/{image_id}.{extension}"
    
    def upload_image(self, image_data: bytes, user_id: str, image_id: str, 
                    content_type: str = 'image/png') -> str:
        """Upload an image to S3"""
        key = self.generate_image_key(user_id, image_id)
        
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_data,
                ContentType=content_type,
                CacheControl='max-age=31536000',  # 1 year cache
                Metadata={
                    'user_id': user_id,
                    'image_id': image_id
                }
            )
            
            # Return the S3 URL (will be accessed via CloudFront)
            return f"s3://{self.bucket_name}/{key}"
            
        except ClientError as e:
            raise Exception(f"Error uploading image to S3: {e.response['Error']['Message']}")
    
    def get_presigned_upload_url(self, user_id: str, image_id: str, 
                                content_type: str = 'image/png', 
                                expires_in: int = 3600) -> Dict[str, str]:
        """Generate a presigned URL for direct upload to S3"""
        key = self.generate_image_key(user_id, image_id)
        
        try:
            response = self.s3.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=key,
                Fields={
                    'Content-Type': content_type,
                    'Cache-Control': 'max-age=31536000',
                    'x-amz-meta-user_id': user_id,
                    'x-amz-meta-image_id': image_id
                },
                Conditions=[
                    {'Content-Type': content_type},
                    ['content-length-range', 0, 10485760]  # Max 10MB
                ],
                ExpiresIn=expires_in
            )
            
            return response
            
        except ClientError as e:
            raise Exception(f"Error generating presigned URL: {e.response['Error']['Message']}")
    
    def delete_image(self, user_id: str, image_id: str) -> bool:
        """Delete an image from S3"""
        key = self.generate_image_key(user_id, image_id)
        
        try:
            self.s3.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            raise Exception(f"Error deleting image from S3: {e.response['Error']['Message']}")
    
    def copy_image(self, source_user_id: str, source_image_id: str,
                   dest_user_id: str, dest_image_id: str) -> str:
        """Copy an image to a new location"""
        source_key = self.generate_image_key(source_user_id, source_image_id)
        dest_key = self.generate_image_key(dest_user_id, dest_image_id)
        
        try:
            self.s3.copy_object(
                Bucket=self.bucket_name,
                CopySource={'Bucket': self.bucket_name, 'Key': source_key},
                Key=dest_key,
                MetadataDirective='REPLACE',
                Metadata={
                    'user_id': dest_user_id,
                    'image_id': dest_image_id
                }
            )
            
            return f"s3://{self.bucket_name}/{dest_key}"
            
        except ClientError as e:
            raise Exception(f"Error copying image in S3: {e.response['Error']['Message']}")


class CloudFrontSigner:
    """Generate CloudFront signed URLs for secure image access"""
    
    def __init__(self):
        self.cloudfront_domain = settings.CLOUDFRONT_DOMAIN
        self.key_pair_id = settings.CLOUDFRONT_KEY_PAIR_ID
        
        # Load private key for signing
        if settings.CLOUDFRONT_PRIVATE_KEY:
            self.private_key = serialization.load_pem_private_key(
                settings.CLOUDFRONT_PRIVATE_KEY.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
        else:
            self.private_key = None
    
    def _create_policy(self, resource: str, expire_time: int) -> str:
        """Create a CloudFront canned policy"""
        policy = {
            "Statement": [{
                "Resource": resource,
                "Condition": {
                    "DateLessThan": {
                        "AWS:EpochTime": expire_time
                    }
                }
            }]
        }
        
        # Remove whitespace
        import json
        return json.dumps(policy, separators=(',', ':'))
    
    def _sign_policy(self, policy: str) -> str:
        """Sign the policy with RSA private key"""
        if not self.private_key:
            raise ValueError("CloudFront private key not configured")
        
        # Sign the policy
        signature = self.private_key.sign(
            policy.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        
        # Base64 encode and make URL-safe
        encoded = base64.b64encode(signature).decode('utf-8')
        return encoded.replace('+', '-').replace('=', '_').replace('/', '~')
    
    def generate_signed_url(self, s3_url: str, expires_in_seconds: int = 600) -> str:
        """Generate a CloudFront signed URL for an S3 object"""
        if not self.cloudfront_domain:
            # Return unsigned URL if CloudFront not configured
            return s3_url.replace(f"s3://{settings.AWS_S3_BUCKET_NAME}/", 
                                f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/")
        
        # Convert S3 URL to CloudFront URL
        key = s3_url.replace(f"s3://{settings.AWS_S3_BUCKET_NAME}/", "")
        cloudfront_url = f"https://{self.cloudfront_domain}/{key}"
        
        if not self.private_key:
            # Return unsigned CloudFront URL if signing not configured
            return cloudfront_url
        
        # Calculate expiration time
        expire_time = int((datetime.utcnow() + timedelta(seconds=expires_in_seconds)).timestamp())
        
        # Create and sign policy
        policy = self._create_policy(cloudfront_url, expire_time)
        signature = self._sign_policy(policy)
        
        # Build signed URL
        signed_url = f"{cloudfront_url}?Expires={expire_time}&Signature={signature}&Key-Pair-Id={self.key_pair_id}"
        
        return signed_url


class ImageStorage:
    """High-level interface for image storage operations"""
    
    def __init__(self):
        self.s3 = S3Client()
        self.cloudfront = CloudFrontSigner()
    
    def store_image(self, image_data: bytes, user_id: str, 
                   content_type: str = 'image/png') -> Tuple[str, str]:
        """Store an image and return (image_id, s3_url)"""
        image_id = str(uuid.uuid4())
        s3_url = self.s3.upload_image(image_data, user_id, image_id, content_type)
        return image_id, s3_url
    
    def get_signed_url(self, s3_url: str, expires_in: int = None) -> str:
        """Get a signed URL for accessing an image"""
        if expires_in is None:
            expires_in = settings.SIGNED_URL_TTL
        
        return self.cloudfront.generate_signed_url(s3_url, expires_in)
    
    def get_upload_url(self, user_id: str) -> Dict[str, str]:
        """Get a presigned URL for direct upload"""
        image_id = str(uuid.uuid4())
        upload_data = self.s3.get_presigned_upload_url(user_id, image_id)
        upload_data['image_id'] = image_id
        return upload_data
    
    def delete_image(self, user_id: str, image_id: str) -> bool:
        """Delete an image from storage"""
        return self.s3.delete_image(user_id, image_id)
    
    def copy_image(self, source_user_id: str, source_image_id: str,
                   dest_user_id: str) -> Tuple[str, str]:
        """Copy an image to a new user's storage"""
        dest_image_id = str(uuid.uuid4())
        s3_url = self.s3.copy_image(
            source_user_id, source_image_id,
            dest_user_id, dest_image_id
        )
        return dest_image_id, s3_url
