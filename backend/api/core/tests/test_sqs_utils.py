"""
Test cases for SQS utilities
"""

import pytest
import json
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from api.core.sqs_utils import SQSClient, JobQueue


class TestSQSClient:
    """Test cases for SQSClient class"""
    
    @pytest.fixture
    def mock_boto_client(self):
        """Mock boto3 SQS client"""
        return Mock()
    
    @pytest.fixture
    def client(self, mock_boto_client):
        """Create SQSClient instance with mocked boto client"""
        with patch('api.core.sqs_utils.boto3.client', return_value=mock_boto_client), \
             patch('api.core.sqs_utils.settings') as mock_settings:
            mock_settings.AWS_REGION = 'us-east-1'
            mock_settings.AWS_ACCESS_KEY_ID = 'test-key'
            mock_settings.AWS_SECRET_ACCESS_KEY = 'test-secret'
            mock_settings.AWS_SQS_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'
            
            client = SQSClient()
            client.sqs = mock_boto_client
            return client
    
    def test_init_sets_attributes(self, client):
        """Test client initialization"""
        assert client.queue_url == 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'
        assert client.sqs is not None
    
    def test_send_message_success(self, client, mock_boto_client):
        """Test successful message sending"""
        mock_boto_client.send_message.return_value = {
            'MessageId': 'msg-123-456',
            'MD5OfMessageBody': 'abc123'
        }
        
        message_body = {'job_id': 'job123', 'action': 'generate'}
        message_id = client.send_message(message_body)
        
        assert message_id == 'msg-123-456'
        
        mock_boto_client.send_message.assert_called_once_with(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/test-queue',
            MessageBody=json.dumps(message_body),
            DelaySeconds=0
        )
    
    def test_send_message_with_delay(self, client, mock_boto_client):
        """Test sending message with delay"""
        mock_boto_client.send_message.return_value = {'MessageId': 'msg-123'}
        
        message_body = {'test': 'data'}
        client.send_message(message_body, delay_seconds=60)
        
        call_args = mock_boto_client.send_message.call_args[1]
        assert call_args['DelaySeconds'] == 60
    
    def test_send_message_error(self, client, mock_boto_client):
        """Test handling send message errors"""
        mock_boto_client.send_message.side_effect = ClientError(
            {'Error': {'Message': 'Queue does not exist'}},
            'SendMessage'
        )
        
        with pytest.raises(Exception) as exc_info:
            client.send_message({'test': 'data'})
        
        assert 'Error sending SQS message: Queue does not exist' in str(exc_info.value)
    
    def test_receive_messages_success(self, client, mock_boto_client):
        """Test successful message receiving"""
        mock_boto_client.receive_message.return_value = {
            'Messages': [
                {
                    'MessageId': 'msg-1',
                    'ReceiptHandle': 'receipt-1',
                    'Body': json.dumps({'job_id': 'job1'}),
                    'Attributes': {'ApproximateReceiveCount': '1'}
                },
                {
                    'MessageId': 'msg-2',
                    'ReceiptHandle': 'receipt-2',
                    'Body': json.dumps({'job_id': 'job2'}),
                    'Attributes': {'ApproximateReceiveCount': '2'}
                }
            ]
        }
        
        messages = client.receive_messages(max_messages=2)
        
        assert len(messages) == 2
        assert messages[0]['message_id'] == 'msg-1'
        assert messages[0]['receipt_handle'] == 'receipt-1'
        assert messages[0]['body']['job_id'] == 'job1'
        assert messages[0]['attributes']['ApproximateReceiveCount'] == '1'
        
        mock_boto_client.receive_message.assert_called_once_with(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/test-queue',
            MaxNumberOfMessages=2,
            WaitTimeSeconds=20,
            MessageAttributeNames=['All']
        )
    
    def test_receive_messages_empty(self, client, mock_boto_client):
        """Test receiving when no messages available"""
        mock_boto_client.receive_message.return_value = {}
        
        messages = client.receive_messages()
        
        assert messages == []
    
    def test_receive_messages_custom_wait_time(self, client, mock_boto_client):
        """Test receiving with custom wait time"""
        mock_boto_client.receive_message.return_value = {'Messages': []}
        
        client.receive_messages(max_messages=5, wait_time_seconds=10)
        
        call_args = mock_boto_client.receive_message.call_args[1]
        assert call_args['MaxNumberOfMessages'] == 5
        assert call_args['WaitTimeSeconds'] == 10
    
    def test_receive_messages_error(self, client, mock_boto_client):
        """Test handling receive message errors"""
        mock_boto_client.receive_message.side_effect = ClientError(
            {'Error': {'Message': 'Access denied'}},
            'ReceiveMessage'
        )
        
        with pytest.raises(Exception) as exc_info:
            client.receive_messages()
        
        assert 'Error receiving SQS messages: Access denied' in str(exc_info.value)
    
    def test_delete_message_success(self, client, mock_boto_client):
        """Test successful message deletion"""
        result = client.delete_message('receipt-handle-123')
        
        assert result is True
        
        mock_boto_client.delete_message.assert_called_once_with(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/test-queue',
            ReceiptHandle='receipt-handle-123'
        )
    
    def test_delete_message_error(self, client, mock_boto_client):
        """Test handling delete message errors"""
        mock_boto_client.delete_message.side_effect = ClientError(
            {'Error': {'Message': 'Receipt handle expired'}},
            'DeleteMessage'
        )
        
        with pytest.raises(Exception) as exc_info:
            client.delete_message('expired-handle')
        
        assert 'Error deleting SQS message: Receipt handle expired' in str(exc_info.value)
    
    def test_change_message_visibility_success(self, client, mock_boto_client):
        """Test successful visibility timeout change"""
        result = client.change_message_visibility('receipt-123', 300)
        
        assert result is True
        
        mock_boto_client.change_message_visibility.assert_called_once_with(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/test-queue',
            ReceiptHandle='receipt-123',
            VisibilityTimeout=300
        )
    
    def test_change_message_visibility_error(self, client, mock_boto_client):
        """Test handling visibility change errors"""
        mock_boto_client.change_message_visibility.side_effect = ClientError(
            {'Error': {'Message': 'Invalid receipt handle'}},
            'ChangeMessageVisibility'
        )
        
        with pytest.raises(Exception) as exc_info:
            client.change_message_visibility('invalid-handle', 60)
        
        assert 'Error changing message visibility: Invalid receipt handle' in str(exc_info.value)


class TestJobQueue:
    """Test cases for JobQueue class"""
    
    @pytest.fixture
    def mock_sqs_client(self):
        """Mock SQSClient"""
        return Mock(spec=SQSClient)
    
    @pytest.fixture
    def queue(self, mock_sqs_client):
        """Create JobQueue instance with mocked client"""
        with patch('api.core.sqs_utils.SQSClient', return_value=mock_sqs_client):
            queue = JobQueue()
            queue.sqs = mock_sqs_client
            return queue
    
    def test_enqueue_generation_job(self, queue, mock_sqs_client):
        """Test enqueueing an image generation job"""
        mock_sqs_client.send_message.return_value = 'msg-id-123'
        
        job_data = {
            'job_id': 'job-456',
            'user_id': 'user-789',
            'filters': {'style': 'portrait', 'mood': 'happy'},
            'batch_size': 5,
            'created_at': 1234567890
        }
        
        message_id = queue.enqueue_generation_job(job_data)
        
        assert message_id == 'msg-id-123'
        
        # Verify message structure
        call_args = mock_sqs_client.send_message.call_args[0][0]
        assert call_args['type'] == 'image_generation'
        assert call_args['job_id'] == 'job-456'
        assert call_args['user_id'] == 'user-789'
        assert call_args['filters'] == {'style': 'portrait', 'mood': 'happy'}
        assert call_args['batch_size'] == 5
        assert call_args['timestamp'] == 1234567890
    
    def test_get_next_job_available(self, queue, mock_sqs_client):
        """Test getting next job when available"""
        mock_sqs_client.receive_messages.return_value = [
            {
                'message_id': 'msg-1',
                'receipt_handle': 'receipt-1',
                'body': {'job_id': 'job-1'},
                'attributes': {}
            }
        ]
        
        job = queue.get_next_job()
        
        assert job is not None
        assert job['message_id'] == 'msg-1'
        assert job['body']['job_id'] == 'job-1'
        
        mock_sqs_client.receive_messages.assert_called_once_with(max_messages=1)
    
    def test_get_next_job_none_available(self, queue, mock_sqs_client):
        """Test getting next job when none available"""
        mock_sqs_client.receive_messages.return_value = []
        
        job = queue.get_next_job()
        
        assert job is None
    
    def test_complete_job(self, queue, mock_sqs_client):
        """Test completing a job"""
        mock_sqs_client.delete_message.return_value = True
        
        result = queue.complete_job('receipt-handle-123')
        
        assert result is True
        mock_sqs_client.delete_message.assert_called_once_with('receipt-handle-123')
    
    def test_extend_job_timeout_default(self, queue, mock_sqs_client):
        """Test extending job timeout with default value"""
        mock_sqs_client.change_message_visibility.return_value = True
        
        result = queue.extend_job_timeout('receipt-123')
        
        assert result is True
        mock_sqs_client.change_message_visibility.assert_called_once_with(
            'receipt-123',
            300  # Default 300 seconds
        )
    
    def test_extend_job_timeout_custom(self, queue, mock_sqs_client):
        """Test extending job timeout with custom value"""
        mock_sqs_client.change_message_visibility.return_value = True
        
        result = queue.extend_job_timeout('receipt-123', additional_seconds=600)
        
        assert result is True
        mock_sqs_client.change_message_visibility.assert_called_once_with(
            'receipt-123',
            600
        )