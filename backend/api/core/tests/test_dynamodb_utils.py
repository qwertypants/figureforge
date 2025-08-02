"""
Test cases for DynamoDB utilities
"""

import pytest
import uuid
import time
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from botocore.exceptions import ClientError
from django.test import TestCase
from django.conf import settings

# Configure Django settings for testing
from django.conf import settings
if not settings.configured:
    settings.configure(
        AWS_REGION='us-east-1',
        AWS_ACCESS_KEY_ID='test-key-id',
        AWS_SECRET_ACCESS_KEY='test-secret-key',
        AWS_DYNAMODB_TABLE_NAME='test-table',
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'api',
        ],
        USE_TZ=True,
    )

from api.core.dynamodb_utils import (
    DynamoDBClient, UserRepository, ImageRepository, 
    JobRepository, SubscriptionRepository
)


class TestDynamoDBClient:
    """Test cases for DynamoDBClient class"""
    
    @pytest.fixture
    def mock_table(self):
        """Mock DynamoDB table"""
        return Mock()
    
    @pytest.fixture
    def client(self, mock_table):
        """Create DynamoDBClient instance with mocked table"""
        with patch('api.core.dynamodb_utils.boto3.resource') as mock_resource:
            mock_resource.return_value.Table.return_value = mock_table
            client = DynamoDBClient()
            client.table = mock_table
            return client
    
    def test_serialize_item_converts_floats_to_decimal(self, client):
        """Test that floats are properly converted to Decimals"""
        item = {
            'price': 9.99,
            'quantity': 5,
            'nested': {'value': 1.5}
        }
        
        result = client._serialize_item(item)
        
        assert isinstance(result['price'], Decimal)
        assert result['price'] == Decimal('9.99')
        assert result['quantity'] == 5
        assert isinstance(result['nested']['value'], Decimal)
    
    def test_serialize_item_handles_lists(self, client):
        """Test serialization of lists with mixed types"""
        item = {
            'tags': ['tag1', 'tag2'],
            'prices': [1.5, 2.5, 3.5],
            'mixed': [{'val': 1.0}, 'string', 123]
        }
        
        result = client._serialize_item(item)
        
        assert result['tags'] == ['tag1', 'tag2']
        assert all(isinstance(p, Decimal) for p in result['prices'])
        assert isinstance(result['mixed'][0]['val'], Decimal)
    
    def test_deserialize_item_converts_decimal_to_float(self, client):
        """Test that Decimals are converted back to floats"""
        item = {
            'price': Decimal('9.99'),
            'quantity': 5,
            'nested': {'value': Decimal('1.5')}
        }
        
        result = client._deserialize_item(item)
        
        assert isinstance(result['price'], float)
        assert result['price'] == 9.99
        assert result['quantity'] == 5
        assert isinstance(result['nested']['value'], float)
    
    def test_put_item_adds_timestamp(self, client, mock_table):
        """Test put_item adds created_at timestamp if not present"""
        item = {'pk': 'USER#123', 'sk': 'PROFILE'}
        
        with patch('time.time', return_value=1234567890):
            result = client.put_item(item)
        
        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args[1]['Item']
        assert call_args['created_at'] == 1234567890
    
    def test_put_item_preserves_existing_timestamp(self, client, mock_table):
        """Test put_item preserves existing created_at timestamp"""
        item = {'pk': 'USER#123', 'sk': 'PROFILE', 'created_at': 9999}
        
        result = client.put_item(item)
        
        call_args = mock_table.put_item.call_args[1]['Item']
        assert call_args['created_at'] == 9999
    
    def test_put_item_handles_client_error(self, client, mock_table):
        """Test put_item raises exception on ClientError"""
        mock_table.put_item.side_effect = ClientError(
            {'Error': {'Message': 'Item size exceeded'}}, 
            'PutItem'
        )
        
        with pytest.raises(Exception) as exc_info:
            client.put_item({'pk': 'TEST', 'sk': 'TEST'})
        
        assert 'Error putting item: Item size exceeded' in str(exc_info.value)
    
    def test_get_item_returns_item(self, client, mock_table):
        """Test get_item returns deserialized item"""
        mock_table.get_item.return_value = {
            'Item': {'pk': 'USER#123', 'sk': 'PROFILE', 'price': Decimal('9.99')}
        }
        
        result = client.get_item('USER#123', 'PROFILE')
        
        assert result['pk'] == 'USER#123'
        assert result['price'] == 9.99
    
    def test_get_item_returns_none_when_not_found(self, client, mock_table):
        """Test get_item returns None when item not found"""
        mock_table.get_item.return_value = {}
        
        result = client.get_item('USER#123', 'PROFILE')
        
        assert result is None
    
    def test_query_items_basic(self, client, mock_table):
        """Test basic query by partition key"""
        mock_table.query.return_value = {
            'Items': [
                {'pk': 'USER#123', 'sk': 'PROFILE'},
                {'pk': 'USER#123', 'sk': 'IMG#abc'}
            ]
        }
        
        items, next_key = client.query_items('USER#123')
        
        assert len(items) == 2
        assert next_key is None
        mock_table.query.assert_called_with(
            KeyConditionExpression='pk = :pk',
            ExpressionAttributeValues={':pk': 'USER#123'}
        )
    
    def test_query_items_with_sk_prefix(self, client, mock_table):
        """Test query with sort key prefix"""
        mock_table.query.return_value = {'Items': []}
        
        client.query_items('USER#123', sk_prefix='IMG#')
        
        mock_table.query.assert_called_with(
            KeyConditionExpression='pk = :pk AND begins_with(sk, :sk_prefix)',
            ExpressionAttributeValues={':pk': 'USER#123', ':sk_prefix': 'IMG#'}
        )
    
    def test_query_items_with_pagination(self, client, mock_table):
        """Test query with limit and pagination"""
        mock_table.query.return_value = {
            'Items': [{'pk': 'USER#123', 'sk': 'IMG#1'}],
            'LastEvaluatedKey': {'pk': 'USER#123', 'sk': 'IMG#1'}
        }
        
        items, next_key = client.query_items('USER#123', limit=1)
        
        assert len(items) == 1
        assert next_key == {'pk': 'USER#123', 'sk': 'IMG#1'}
        assert 'Limit' in mock_table.query.call_args[1]
    
    def test_delete_item_soft_delete(self, client, mock_table):
        """Test delete_item performs soft delete"""
        with patch('time.time', return_value=1234567890):
            result = client.delete_item('USER#123', 'PROFILE')
        
        assert result is True
        mock_table.update_item.assert_called_with(
            Key={'pk': 'USER#123', 'sk': 'PROFILE'},
            UpdateExpression='SET deleted_at = :timestamp',
            ExpressionAttributeValues={':timestamp': 1234567890}
        )
    
    def test_query_gsi_basic(self, client, mock_table):
        """Test querying Global Secondary Index"""
        mock_table.query.return_value = {
            'Items': [{'pk': 'EMAIL#test@example.com', 'sk': 'USER#123'}]
        }
        
        items, next_key = client.query_gsi('byEmail', 'EMAIL#test@example.com')
        
        assert len(items) == 1
        mock_table.query.assert_called_with(
            IndexName='byEmail',
            KeyConditionExpression='pk = :pk',
            ExpressionAttributeValues={':pk': 'EMAIL#test@example.com'}
        )


class TestUserRepository:
    """Test cases for UserRepository"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock DynamoDBClient"""
        return Mock(spec=DynamoDBClient)
    
    @pytest.fixture
    def repo(self, mock_db_client):
        """Create UserRepository with mocked client"""
        with patch('api.core.dynamodb_utils.DynamoDBClient', return_value=mock_db_client):
            repo = UserRepository()
            repo.db = mock_db_client
            return repo
    
    def test_create_user(self, repo, mock_db_client):
        """Test creating a new user"""
        with patch('time.time', return_value=1234567890):
            result = repo.create_user('user123', 'test@example.com', 'testuser')
        
        # Should create two items: user and email index
        assert mock_db_client.put_item.call_count == 2
        
        # Check user item
        user_call = mock_db_client.put_item.call_args_list[0][0][0]
        assert user_call['pk'] == 'USER#user123'
        assert user_call['sk'] == 'PROFILE'
        assert user_call['email'] == 'test@example.com'
        assert user_call['username'] == 'testuser'
        assert user_call['role'] == 'user'
        assert user_call['quota_used'] == 0
        
        # Check email index
        email_call = mock_db_client.put_item.call_args_list[1][0][0]
        assert email_call['pk'] == 'EMAIL#test@example.com'
        assert email_call['sk'] == 'USER#user123'
    
    def test_create_user_auto_username(self, repo, mock_db_client):
        """Test creating user with auto-generated username"""
        result = repo.create_user('user123456', 'test@example.com')
        
        user_call = mock_db_client.put_item.call_args_list[0][0][0]
        assert user_call['username'] == 'user_user1234'
    
    def test_get_user(self, repo, mock_db_client):
        """Test getting user by ID"""
        mock_db_client.get_item.return_value = {'user_id': 'user123'}
        
        result = repo.get_user('user123')
        
        mock_db_client.get_item.assert_called_with('USER#user123', 'PROFILE')
        assert result == {'user_id': 'user123'}
    
    def test_get_user_by_email(self, repo, mock_db_client):
        """Test getting user by email"""
        mock_db_client.query_gsi.return_value = (
            [{'pk': 'EMAIL#test@example.com', 'sk': 'USER#user123'}], 
            None
        )
        mock_db_client.get_item.return_value = {'user_id': 'user123'}
        
        result = repo.get_user_by_email('test@example.com')
        
        mock_db_client.query_gsi.assert_called_with('byEmail', 'EMAIL#test@example.com', limit=1)
        mock_db_client.get_item.assert_called_with('USER#user123', 'PROFILE')
        assert result == {'user_id': 'user123'}
    
    def test_get_user_by_email_not_found(self, repo, mock_db_client):
        """Test getting user by email when not found"""
        mock_db_client.query_gsi.return_value = ([], None)
        
        result = repo.get_user_by_email('notfound@example.com')
        
        assert result is None
    
    def test_update_user(self, repo, mock_db_client):
        """Test updating user profile"""
        mock_db_client.get_item.return_value = {
            'pk': 'USER#user123',
            'sk': 'PROFILE',
            'username': 'oldname'
        }
        
        result = repo.update_user('user123', {'username': 'newname'})
        
        mock_db_client.get_item.assert_called_with('USER#user123', 'PROFILE')
        updated_item = mock_db_client.put_item.call_args[0][0]
        assert updated_item['username'] == 'newname'
    
    def test_update_user_not_found(self, repo, mock_db_client):
        """Test updating non-existent user raises error"""
        mock_db_client.get_item.return_value = None
        
        with pytest.raises(ValueError) as exc_info:
            repo.update_user('user123', {'username': 'newname'})
        
        assert 'User user123 not found' in str(exc_info.value)


class TestImageRepository:
    """Test cases for ImageRepository"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock DynamoDBClient"""
        return Mock(spec=DynamoDBClient)
    
    @pytest.fixture
    def repo(self, mock_db_client):
        """Create ImageRepository with mocked client"""
        with patch('api.core.dynamodb_utils.DynamoDBClient', return_value=mock_db_client):
            repo = ImageRepository()
            repo.db = mock_db_client
            return repo
    
    def test_create_image(self, repo, mock_db_client):
        """Test creating a new image record"""
        with patch('api.core.dynamodb_utils.uuid.uuid4', return_value='image123'), \
             patch('time.time', return_value=1234567890):
            
            image_data = {
                'user_id': 'user123',
                'url': 'https://example.com/image.jpg',
                'tags': ['portrait', 'digital'],
                'prompt_json': {'style': 'realistic'},
                'cost_cents': 50
            }
            
            result = repo.create_image(image_data)
        
        # Should create: main image + 2 tag indexes + 1 user index
        assert mock_db_client.put_item.call_count == 4
        
        # Check main image
        image_call = mock_db_client.put_item.call_args_list[0][0][0]
        assert image_call['pk'] == 'IMG#image123'
        assert image_call['sk'] == 'META'
        assert image_call['url'] == 'https://example.com/image.jpg'
        assert image_call['tags'] == ['portrait', 'digital']
        assert image_call['favorited_count'] == 0
        assert image_call['public'] is True
        
        # Check tag indexes
        tag_calls = [call[0][0] for call in mock_db_client.put_item.call_args_list[1:3]]
        tag_pks = sorted([call['pk'] for call in tag_calls])
        assert tag_pks == ['TAG#digital', 'TAG#portrait']
        
        # Check user index
        user_index = mock_db_client.put_item.call_args_list[3][0][0]
        assert user_index['pk'] == 'USER#user123'
        assert user_index['sk'] == 'IMG#image123'
    
    def test_create_image_without_user(self, repo, mock_db_client):
        """Test creating image without user_id"""
        with patch('api.core.dynamodb_utils.uuid.uuid4', return_value='image123'):
            image_data = {
                'url': 'https://example.com/image.jpg',
                'tags': []
            }
            
            result = repo.create_image(image_data)
        
        # Should only create main image (no tags or user index)
        assert mock_db_client.put_item.call_count == 1
    
    def test_get_image(self, repo, mock_db_client):
        """Test getting image by ID"""
        mock_db_client.get_item.return_value = {'image_id': 'image123'}
        
        result = repo.get_image('image123')
        
        mock_db_client.get_item.assert_called_with('IMG#image123', 'META')
        assert result == {'image_id': 'image123'}
    
    def test_get_images_by_tag(self, repo, mock_db_client):
        """Test getting images by tag"""
        mock_db_client.query_items.return_value = (
            [{'sk': 'IMG#image1'}, {'sk': 'IMG#image2'}],
            None
        )
        mock_db_client.get_item.side_effect = [
            {'image_id': 'image1', 'url': 'url1'},
            {'image_id': 'image2', 'url': 'url2', 'deleted_at': 123},  # Deleted
        ]
        
        images, cursor = repo.get_images_by_tag('portrait', limit=10)
        
        # Should only return non-deleted image
        assert len(images) == 1
        assert images[0]['image_id'] == 'image1'
        assert cursor is None
    
    def test_get_images_by_tag_with_pagination(self, repo, mock_db_client):
        """Test getting images by tag with pagination"""
        mock_db_client.query_items.return_value = (
            [{'sk': 'IMG#image1'}],
            {'pk': 'TAG#portrait', 'sk': 'IMG#image1'}
        )
        mock_db_client.get_item.return_value = {'image_id': 'image1'}
        
        images, cursor = repo.get_images_by_tag('portrait', cursor='IMG#prev')
        
        assert cursor == 'IMG#image1'
        mock_db_client.query_items.assert_called_with(
            'TAG#portrait',
            limit=20,
            last_evaluated_key={'pk': 'TAG#portrait', 'sk': 'IMG#prev'}
        )
    
    def test_get_user_images(self, repo, mock_db_client):
        """Test getting images by user"""
        mock_db_client.query_gsi.return_value = (
            [
                {'sk': 'IMG#image1'}, 
                {'sk': 'PROFILE'},  # Non-image item
                {'sk': 'IMG#image2'}
            ],
            None
        )
        mock_db_client.get_item.side_effect = [
            {'image_id': 'image1'},
            {'image_id': 'image2'}
        ]
        
        images, cursor = repo.get_user_images('user123')
        
        assert len(images) == 2
        mock_db_client.query_gsi.assert_called_with(
            'imagesByUser', 
            'USER#user123', 
            limit=20, 
            last_evaluated_key=None
        )


class TestJobRepository:
    """Test cases for JobRepository"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock DynamoDBClient"""
        return Mock(spec=DynamoDBClient)
    
    @pytest.fixture
    def repo(self, mock_db_client):
        """Create JobRepository with mocked client"""
        with patch('api.core.dynamodb_utils.DynamoDBClient', return_value=mock_db_client):
            repo = JobRepository()
            repo.db = mock_db_client
            return repo
    
    def test_create_job(self, repo, mock_db_client):
        """Test creating a new generation job"""
        with patch('api.core.dynamodb_utils.uuid.uuid4', return_value='job123'), \
             patch('time.time', return_value=1234567890):
            
            filters = {'style': 'portrait', 'mood': 'happy'}
            result = repo.create_job('user123', filters, batch_size=5)
        
        # Should create job and status index
        assert mock_db_client.put_item.call_count == 2
        
        # Check job item
        job_call = mock_db_client.put_item.call_args_list[0][0][0]
        assert job_call['pk'] == 'USER#user123'
        assert job_call['sk'] == 'JOB#job123'
        assert job_call['status'] == 'queued'
        assert job_call['batch_size'] == 5
        assert job_call['image_ids'] == []
        
        # Check status index
        status_call = mock_db_client.put_item.call_args_list[1][0][0]
        assert status_call['pk'] == 'JOBSTATUS#queued'
        assert status_call['sk'] == '1234567890'
    
    def test_get_job(self, repo, mock_db_client):
        """Test getting job by ID"""
        mock_db_client.get_item.return_value = {'job_id': 'job123'}
        
        result = repo.get_job('user123', 'job123')
        
        mock_db_client.get_item.assert_called_with('USER#user123', 'JOB#job123')
        assert result == {'job_id': 'job123'}
    
    def test_update_job_status(self, repo, mock_db_client):
        """Test updating job status"""
        mock_db_client.get_item.return_value = {
            'pk': 'USER#user123',
            'sk': 'JOB#job123',
            'job_id': 'job123',
            'status': 'queued',
            'created_at': 1234567890
        }
        
        with patch('time.time', return_value=1234567900):
            result = repo.update_job_status(
                'user123', 
                'job123', 
                'completed',
                image_ids=['img1', 'img2']
            )
        
        # Should delete old status index, update job, create new status index
        assert mock_db_client.delete_item.call_count == 1
        assert mock_db_client.put_item.call_count == 2
        
        # Check delete call
        mock_db_client.delete_item.assert_called_with(
            'JOBSTATUS#queued', 
            '1234567890'
        )
        
        # Check updated job
        job_update = mock_db_client.put_item.call_args_list[0][0][0]
        assert job_update['status'] == 'completed'
        assert job_update['image_ids'] == ['img1', 'img2']
        assert job_update['updated_at'] == 1234567900
    
    def test_update_job_status_not_found(self, repo, mock_db_client):
        """Test updating non-existent job raises error"""
        mock_db_client.get_item.return_value = None
        
        with pytest.raises(ValueError) as exc_info:
            repo.update_job_status('user123', 'job123', 'completed')
        
        assert 'Job job123 not found' in str(exc_info.value)


class TestSubscriptionRepository:
    """Test cases for SubscriptionRepository"""
    
    @pytest.fixture
    def mock_db_client(self):
        """Mock DynamoDBClient"""
        return Mock(spec=DynamoDBClient)
    
    @pytest.fixture
    def repo(self, mock_db_client):
        """Create SubscriptionRepository with mocked client"""
        with patch('api.core.dynamodb_utils.DynamoDBClient', return_value=mock_db_client):
            repo = SubscriptionRepository()
            repo.db = mock_db_client
            return repo
    
    def test_create_subscription(self, repo, mock_db_client):
        """Test creating a new subscription"""
        with patch('time.time', return_value=1234567890):
            result = repo.create_subscription(
                'user123',
                'sub_stripe123',
                'pro',
                'active',
                1234567890
            )
        
        # Should create subscription and Stripe index
        assert mock_db_client.put_item.call_count == 2
        
        # Check subscription item
        sub_call = mock_db_client.put_item.call_args_list[0][0][0]
        assert sub_call['pk'] == 'USER#user123'
        assert sub_call['sk'] == 'SUB#sub_stripe123'
        assert sub_call['plan_id'] == 'pro'
        assert sub_call['status'] == 'active'
        
        # Check Stripe index
        index_call = mock_db_client.put_item.call_args_list[1][0][0]
        assert index_call['pk'] == 'SUB#sub_stripe123'
        assert index_call['sk'] == 'USER#user123'
    
    def test_get_subscription(self, repo, mock_db_client):
        """Test getting subscription by ID"""
        mock_db_client.get_item.return_value = {'subscription_id': 'sub123'}
        
        result = repo.get_subscription('user123', 'sub123')
        
        mock_db_client.get_item.assert_called_with('USER#user123', 'SUB#sub123')
        assert result == {'subscription_id': 'sub123'}
    
    def test_get_user_subscriptions(self, repo, mock_db_client):
        """Test getting all subscriptions for a user"""
        mock_db_client.query_items.return_value = (
            [
                {'subscription_id': 'sub1', 'status': 'active'},
                {'subscription_id': 'sub2', 'status': 'canceled'},
                {'sk': 'SUB#sub3'}  # Item without subscription_id
            ],
            None
        )
        
        result = repo.get_user_subscriptions('user123')
        
        assert len(result) == 2
        assert all('subscription_id' in sub for sub in result)
    
    def test_get_active_subscription(self, repo, mock_db_client):
        """Test getting the active subscription for a user"""
        mock_db_client.query_items.return_value = (
            [
                {'subscription_id': 'sub1', 'status': 'canceled'},
                {'subscription_id': 'sub2', 'status': 'active'},
                {'subscription_id': 'sub3', 'status': 'past_due'}
            ],
            None
        )
        
        result = repo.get_active_subscription('user123')
        
        assert result['subscription_id'] == 'sub2'
        assert result['status'] == 'active'
    
    def test_get_active_subscription_none_active(self, repo, mock_db_client):
        """Test getting active subscription when none are active"""
        mock_db_client.query_items.return_value = (
            [
                {'subscription_id': 'sub1', 'status': 'canceled'},
                {'subscription_id': 'sub2', 'status': 'past_due'}
            ],
            None
        )
        
        result = repo.get_active_subscription('user123')
        
        assert result is None
    
    def test_update_subscription(self, repo, mock_db_client):
        """Test updating subscription"""
        mock_db_client.get_item.return_value = {
            'pk': 'USER#user123',
            'sk': 'SUB#sub123',
            'subscription_id': 'sub123',
            'status': 'active',
            'plan_id': 'hobby'
        }
        
        with patch('time.time', return_value=1234567900):
            result = repo.update_subscription(
                'user123',
                'sub123',
                {'status': 'canceled', 'plan_id': 'pro'}
            )
        
        updated_item = mock_db_client.put_item.call_args[0][0]
        assert updated_item['status'] == 'canceled'
        assert updated_item['plan_id'] == 'pro'
        assert updated_item['updated_at'] == 1234567900
    
    def test_update_subscription_not_found(self, repo, mock_db_client):
        """Test updating non-existent subscription raises error"""
        mock_db_client.get_item.return_value = None
        
        with pytest.raises(ValueError) as exc_info:
            repo.update_subscription('user123', 'sub123', {'status': 'canceled'})
        
        assert 'Subscription sub123 not found' in str(exc_info.value)