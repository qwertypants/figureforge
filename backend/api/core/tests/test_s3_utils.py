"""
Test cases for S3 utilities and CloudFront signed URLs
"""

import pytest
import uuid
import json
import base64
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

from api.core.s3_utils import S3Client, CloudFrontSigner, ImageStorage


class TestS3Client:
    """Test cases for S3Client class"""
    
    @pytest.fixture
    def mock_boto_client(self):
        """Mock boto3 S3 client"""
        return Mock()
    
    @pytest.fixture
    def client(self, mock_boto_client):
        """Create S3Client instance with mocked boto client"""
        with patch('api.core.s3_utils.boto3.client', return_value=mock_boto_client), \
             patch('api.core.s3_utils.settings') as mock_settings:
            mock_settings.AWS_REGION = 'us-east-1'
            mock_settings.AWS_ACCESS_KEY_ID = 'test-key'
            mock_settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
            mock_settings.AWS_S3_BUCKET_NAME = 'test-bucket'
            
            client = S3Client()
            client.s3 = mock_boto_client
            return client
    
    def test_init_sets_attributes(self, client):
        """Test client initialization"""
        assert client.bucket_name == 'test-bucket'
        assert client.s3 is not None
    
    def test_generate_image_key(self, client):
        """Test generating S3 key for images"""
        key = client.generate_image_key('user123', 'image456')
        assert key == 'images/user123/image456.png'
        
        key_with_ext = client.generate_image_key('user123', 'image456', 'jpg')
        assert key_with_ext == 'images/user123/image456.jpg'
    
    def test_upload_image_success(self, client, mock_boto_client):
        """Test successful image upload"""
        image_data = b'fake-image-data'
        user_id = 'user123'
        image_id = 'image456'
        
        result = client.upload_image(image_data, user_id, image_id)
        
        mock_boto_client.put_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='images/user123/image456.png',
            Body=image_data,
            ContentType='image/png',
            CacheControl='max-age=31536000',
            Metadata={
                'user_id': user_id,
                'image_id': image_id
            }
        )
        
        assert result == 's3://test-bucket/images/user123/image456.png'
    
    def test_upload_image_with_content_type(self, client, mock_boto_client):
        """Test image upload with custom content type"""
        image_data = b'fake-jpeg-data'
        
        result = client.upload_image(image_data, 'user123', 'image456', 'image/jpeg')
        
        call_args = mock_boto_client.put_object.call_args[1]
        assert call_args['ContentType'] == 'image/jpeg'
    
    def test_upload_image_error(self, client, mock_boto_client):
        """Test handling upload errors"""
        mock_boto_client.put_object.side_effect = ClientError(
            {'Error': {'Message': 'Access Denied'}},
            'PutObject'
        )
        
        with pytest.raises(Exception) as exc_info:
            client.upload_image(b'data', 'user123', 'image456')
        
        assert 'Error uploading image to S3: Access Denied' in str(exc_info.value)
    
    def test_get_presigned_upload_url_success(self, client, mock_boto_client):
        """Test generating presigned upload URL"""
        mock_response = {
            'url': 'https://test-bucket.s3.amazonaws.com/',
            'fields': {
                'key': 'images/user123/image456.png',
                'AWSAccessKeyId': 'test-key',
                'policy': 'encoded-policy',
                'signature': 'signature'
            }
        }
        mock_boto_client.generate_presigned_post.return_value = mock_response
        
        result = client.get_presigned_upload_url('user123', 'image456')
        
        mock_boto_client.generate_presigned_post.assert_called_once()
        call_args = mock_boto_client.generate_presigned_post.call_args[1]
        assert call_args['Bucket'] == 'test-bucket'
        assert call_args['Key'] == 'images/user123/image456.png'
        assert call_args['ExpiresIn'] == 3600
        
        # Check fields
        assert call_args['Fields']['Content-Type'] == 'image/png'
        assert call_args['Fields']['x-amz-meta-user_id'] == 'user123'
        assert call_args['Fields']['x-amz-meta-image_id'] == 'image456'
        
        # Check conditions
        conditions = call_args['Conditions']
        assert {'Content-Type': 'image/png'} in conditions
        assert ['content-length-range', 0, 10485760] in conditions
        
        assert result == mock_response
    
    def test_get_presigned_upload_url_custom_params(self, client, mock_boto_client):
        """Test presigned URL with custom parameters"""
        mock_boto_client.generate_presigned_post.return_value = {}
        
        client.get_presigned_upload_url(
            'user123', 
            'image456',
            content_type='image/jpeg',
            expires_in=7200
        )
        
        call_args = mock_boto_client.generate_presigned_post.call_args[1]
        assert call_args['Fields']['Content-Type'] == 'image/jpeg'
        assert call_args['ExpiresIn'] == 7200
    
    def test_delete_image_success(self, client, mock_boto_client):
        """Test successful image deletion"""
        result = client.delete_image('user123', 'image456')
        
        mock_boto_client.delete_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='images/user123/image456.png'
        )
        
        assert result is True
    
    def test_delete_image_error(self, client, mock_boto_client):
        """Test handling deletion errors"""
        mock_boto_client.delete_object.side_effect = ClientError(
            {'Error': {'Message': 'NoSuchKey'}},
            'DeleteObject'
        )
        
        with pytest.raises(Exception) as exc_info:
            client.delete_image('user123', 'image456')
        
        assert 'Error deleting image from S3: NoSuchKey' in str(exc_info.value)
    
    def test_copy_image_success(self, client, mock_boto_client):
        """Test successful image copy"""
        result = client.copy_image('user123', 'image456', 'user789', 'image999')
        
        mock_boto_client.copy_object.assert_called_once_with(
            Bucket='test-bucket',
            CopySource={'Bucket': 'test-bucket', 'Key': 'images/user123/image456.png'},
            Key='images/user789/image999.png',
            MetadataDirective='REPLACE',
            Metadata={
                'user_id': 'user789',
                'image_id': 'image999'
            }
        )
        
        assert result == 's3://test-bucket/images/user789/image999.png'
    
    def test_copy_image_error(self, client, mock_boto_client):
        """Test handling copy errors"""
        mock_boto_client.copy_object.side_effect = ClientError(
            {'Error': {'Message': 'NoSuchKey'}},
            'CopyObject'
        )
        
        with pytest.raises(Exception) as exc_info:
            client.copy_image('user123', 'image456', 'user789', 'image999')
        
        assert 'Error copying image in S3: NoSuchKey' in str(exc_info.value)


class TestCloudFrontSigner:
    """Test cases for CloudFrontSigner class"""
    
    @pytest.fixture
    def mock_private_key(self):
        """Mock RSA private key"""
        key = Mock()
        key.sign.return_value = b'fake-signature'
        return key
    
    @pytest.fixture
    def signer(self, mock_private_key):
        """Create CloudFrontSigner instance"""
        with patch('api.core.s3_utils.settings') as mock_settings:
            mock_settings.CLOUDFRONT_DOMAIN = 'cdn.example.com'
            mock_settings.CLOUDFRONT_KEY_PAIR_ID = 'KEYPAIRID123'
            mock_settings.CLOUDFRONT_PRIVATE_KEY = 'fake-private-key'
            mock_settings.AWS_S3_BUCKET_NAME = 'test-bucket'
            
            with patch('api.core.s3_utils.serialization.load_pem_private_key', 
                      return_value=mock_private_key):
                signer = CloudFrontSigner()
                return signer
    
    def test_init_loads_private_key(self, signer):
        """Test signer initialization loads private key"""
        assert signer.cloudfront_domain == 'cdn.example.com'
        assert signer.key_pair_id == 'KEYPAIRID123'
        assert signer.private_key is not None
    
    def test_init_without_private_key(self):
        """Test signer initialization without private key"""
        with patch('api.core.s3_utils.settings') as mock_settings:
            mock_settings.CLOUDFRONT_DOMAIN = 'cdn.example.com'
            mock_settings.CLOUDFRONT_KEY_PAIR_ID = 'KEYPAIRID123'
            mock_settings.CLOUDFRONT_PRIVATE_KEY = None
            
            signer = CloudFrontSigner()
            assert signer.private_key is None
    
    def test_create_policy(self, signer):
        """Test creating CloudFront policy"""
        resource = 'https://cdn.example.com/test.jpg'
        expire_time = 1234567890
        
        policy = signer._create_policy(resource, expire_time)
        
        # Parse to verify structure
        policy_dict = json.loads(policy)
        statement = policy_dict['Statement'][0]
        assert statement['Resource'] == resource
        assert statement['Condition']['DateLessThan']['AWS:EpochTime'] == expire_time
        
        # Verify no whitespace
        assert ' ' not in policy
    
    def test_sign_policy(self, signer, mock_private_key):
        """Test signing policy"""
        policy = '{"test":"policy"}'
        
        # Mock base64 encoding
        with patch('base64.b64encode', return_value=b'encoded+signature=with/chars'):
            result = signer._sign_policy(policy)
        
        mock_private_key.sign.assert_called_once()
        
        # Verify URL-safe encoding
        assert '+' not in result
        assert '=' not in result
        assert '/' not in result
        assert '-' in result  # + becomes -
        assert '_' in result  # = becomes _
        assert '~' in result  # / becomes ~
    
    def test_sign_policy_no_private_key(self):
        """Test signing policy without private key raises error"""
        with patch('api.core.s3_utils.settings') as mock_settings:
            mock_settings.CLOUDFRONT_PRIVATE_KEY = None
            signer = CloudFrontSigner()
            
            with pytest.raises(ValueError) as exc_info:
                signer._sign_policy('policy')
            
            assert 'CloudFront private key not configured' in str(exc_info.value)
    
    def test_generate_signed_url_with_cloudfront(self, signer):
        """Test generating signed CloudFront URL"""
        s3_url = 's3://test-bucket/images/user123/image456.png'
        
        # Calculate expected expire time (base time + 600 seconds)
        base_time = datetime(2023, 1, 1, 0, 0, 0)
        expected_expire_time = int((base_time + timedelta(seconds=600)).timestamp())
        
        with patch('api.core.s3_utils.settings') as mock_settings:
            # Mock settings for URL generation
            mock_settings.AWS_S3_BUCKET_NAME = 'test-bucket'
            
            with patch('api.core.s3_utils.datetime') as mock_datetime:
                # Import the real datetime module classes
                from datetime import datetime as real_datetime, timedelta as real_timedelta
                # Set datetime to be the real class but with mocked utcnow
                mock_datetime.utcnow.return_value = base_time
                mock_datetime.side_effect = lambda *args, **kwargs: real_datetime(*args, **kwargs)
                
                with patch.object(signer, '_sign_policy', return_value='fake-signature'):
                    result = signer.generate_signed_url(s3_url, expires_in_seconds=600)
        
        # Should convert to CloudFront URL and add signature
        assert result.startswith('https://cdn.example.com/images/user123/image456.png')
        assert f'Expires={expected_expire_time}' in result
        assert 'Signature=fake-signature' in result
        assert 'Key-Pair-Id=KEYPAIRID123' in result
    
    def test_generate_signed_url_no_cloudfront_domain(self):
        """Test generating URL when CloudFront not configured"""
        with patch('api.core.s3_utils.settings') as mock_settings:
            mock_settings.CLOUDFRONT_DOMAIN = None
            mock_settings.CLOUDFRONT_KEY_PAIR_ID = None
            mock_settings.CLOUDFRONT_PRIVATE_KEY = None
            mock_settings.AWS_S3_BUCKET_NAME = 'test-bucket'
            
            signer = CloudFrontSigner()
            s3_url = 's3://test-bucket/images/test.png'
            
            result = signer.generate_signed_url(s3_url)
            
            # Should return S3 HTTPS URL
            assert result == 'https://test-bucket.s3.amazonaws.com/images/test.png'
    
    def test_generate_signed_url_no_private_key(self, signer):
        """Test generating unsigned CloudFront URL when key not configured"""
        signer.private_key = None
        s3_url = 's3://test-bucket/images/test.png'
        
        with patch('api.core.s3_utils.settings') as mock_settings:
            mock_settings.AWS_S3_BUCKET_NAME = 'test-bucket'
            
            result = signer.generate_signed_url(s3_url)
        
        # Should return unsigned CloudFront URL
        assert result == 'https://cdn.example.com/images/test.png'
        assert 'Signature' not in result


class TestImageStorage:
    """Test cases for ImageStorage class"""
    
    @pytest.fixture
    def mock_s3_client(self):
        """Mock S3Client"""
        return Mock(spec=S3Client)
    
    @pytest.fixture
    def mock_cloudfront_signer(self):
        """Mock CloudFrontSigner"""
        return Mock(spec=CloudFrontSigner)
    
    @pytest.fixture
    def storage(self, mock_s3_client, mock_cloudfront_signer):
        """Create ImageStorage instance with mocked dependencies"""
        with patch('api.core.s3_utils.S3Client', return_value=mock_s3_client), \
             patch('api.core.s3_utils.CloudFrontSigner', return_value=mock_cloudfront_signer):
            storage = ImageStorage()
            storage.s3 = mock_s3_client
            storage.cloudfront = mock_cloudfront_signer
            return storage
    
    def test_store_image(self, storage, mock_s3_client):
        """Test storing an image"""
        with patch('api.core.s3_utils.uuid.uuid4', return_value='generated-uuid'):
            mock_s3_client.upload_image.return_value = 's3://bucket/images/user123/generated-uuid.png'
            
            image_data = b'fake-image-data'
            image_id, s3_url = storage.store_image(image_data, 'user123')
        
        assert image_id == 'generated-uuid'
        assert s3_url == 's3://bucket/images/user123/generated-uuid.png'
        
        mock_s3_client.upload_image.assert_called_once_with(
            image_data,
            'user123',
            'generated-uuid',
            'image/png'
        )
    
    def test_store_image_with_content_type(self, storage, mock_s3_client):
        """Test storing image with custom content type"""
        with patch('api.core.s3_utils.uuid.uuid4', return_value='generated-uuid'):
            mock_s3_client.upload_image.return_value = 's3://bucket/test.jpg'
            
            storage.store_image(b'data', 'user123', 'image/jpeg')
        
        call_args = mock_s3_client.upload_image.call_args[0]
        assert call_args[3] == 'image/jpeg'
    
    def test_get_signed_url(self, storage, mock_cloudfront_signer):
        """Test getting signed URL"""
        mock_cloudfront_signer.generate_signed_url.return_value = 'https://cdn.example.com/signed'
        
        with patch('api.core.s3_utils.settings') as mock_settings:
            mock_settings.SIGNED_URL_TTL = 3600
            
            result = storage.get_signed_url('s3://bucket/test.png')
        
        mock_cloudfront_signer.generate_signed_url.assert_called_once_with(
            's3://bucket/test.png',
            3600
        )
        assert result == 'https://cdn.example.com/signed'
    
    def test_get_signed_url_custom_expiry(self, storage, mock_cloudfront_signer):
        """Test getting signed URL with custom expiry"""
        mock_cloudfront_signer.generate_signed_url.return_value = 'https://cdn.example.com/signed'
        
        result = storage.get_signed_url('s3://bucket/test.png', expires_in=7200)
        
        mock_cloudfront_signer.generate_signed_url.assert_called_once_with(
            's3://bucket/test.png',
            7200
        )
    
    def test_get_upload_url(self, storage, mock_s3_client):
        """Test getting presigned upload URL"""
        with patch('api.core.s3_utils.uuid.uuid4', return_value='upload-uuid'):
            mock_s3_client.get_presigned_upload_url.return_value = {
                'url': 'https://bucket.s3.amazonaws.com',
                'fields': {'key': 'test'}
            }
            
            result = storage.get_upload_url('user123')
        
        assert result['image_id'] == 'upload-uuid'
        assert result['url'] == 'https://bucket.s3.amazonaws.com'
        assert result['fields'] == {'key': 'test'}
        
        mock_s3_client.get_presigned_upload_url.assert_called_once_with(
            'user123',
            'upload-uuid'
        )
    
    def test_delete_image(self, storage, mock_s3_client):
        """Test deleting an image"""
        mock_s3_client.delete_image.return_value = True
        
        result = storage.delete_image('user123', 'image456')
        
        assert result is True
        mock_s3_client.delete_image.assert_called_once_with('user123', 'image456')
    
    def test_copy_image(self, storage, mock_s3_client):
        """Test copying an image"""
        with patch('api.core.s3_utils.uuid.uuid4', return_value='new-image-id'):
            mock_s3_client.copy_image.return_value = 's3://bucket/images/user789/new-image-id.png'
            
            dest_id, s3_url = storage.copy_image('user123', 'image456', 'user789')
        
        assert dest_id == 'new-image-id'
        assert s3_url == 's3://bucket/images/user789/new-image-id.png'
        
        mock_s3_client.copy_image.assert_called_once_with(
            'user123',
            'image456',
            'user789',
            'new-image-id'
        )