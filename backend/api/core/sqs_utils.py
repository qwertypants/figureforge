"""
SQS utilities for managing job queues
Handles sending and receiving messages for image generation jobs
"""

import json
import boto3
from typing import Dict, List, Optional
from django.conf import settings
from botocore.exceptions import ClientError


class SQSClient:
    """Wrapper for SQS operations"""
    
    def __init__(self):
        self.sqs = boto3.client(
            'sqs',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.queue_url = settings.AWS_SQS_QUEUE_URL
    
    def send_message(self, message_body: Dict, delay_seconds: int = 0) -> str:
        """Send a message to the SQS queue"""
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                DelaySeconds=delay_seconds
            )
            return response['MessageId']
        except ClientError as e:
            raise Exception(f"Error sending SQS message: {e.response['Error']['Message']}")
    
    def receive_messages(self, max_messages: int = 1, wait_time_seconds: int = 20) -> List[Dict]:
        """Receive messages from the SQS queue"""
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time_seconds,
                MessageAttributeNames=['All']
            )
            
            messages = []
            for message in response.get('Messages', []):
                messages.append({
                    'message_id': message['MessageId'],
                    'receipt_handle': message['ReceiptHandle'],
                    'body': json.loads(message['Body']),
                    'attributes': message.get('Attributes', {})
                })
            
            return messages
        except ClientError as e:
            raise Exception(f"Error receiving SQS messages: {e.response['Error']['Message']}")
    
    def delete_message(self, receipt_handle: str) -> bool:
        """Delete a message from the queue"""
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            return True
        except ClientError as e:
            raise Exception(f"Error deleting SQS message: {e.response['Error']['Message']}")
    
    def change_message_visibility(self, receipt_handle: str, visibility_timeout: int) -> bool:
        """Change the visibility timeout of a message"""
        try:
            self.sqs.change_message_visibility(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
                VisibilityTimeout=visibility_timeout
            )
            return True
        except ClientError as e:
            raise Exception(f"Error changing message visibility: {e.response['Error']['Message']}")


class JobQueue:
    """High-level interface for job queue operations"""
    
    def __init__(self):
        self.sqs = SQSClient()
    
    def enqueue_generation_job(self, job_data: Dict) -> str:
        """Enqueue an image generation job"""
        message = {
            'type': 'image_generation',
            'job_id': job_data['job_id'],
            'user_id': job_data['user_id'],
            'filters': job_data['filters'],
            'batch_size': job_data['batch_size'],
            'timestamp': job_data['created_at']
        }
        
        return self.sqs.send_message(message)
    
    def get_next_job(self) -> Optional[Dict]:
        """Get the next job from the queue"""
        messages = self.sqs.receive_messages(max_messages=1)
        
        if messages:
            return messages[0]
        return None
    
    def complete_job(self, receipt_handle: str) -> bool:
        """Mark a job as completed by deleting it from the queue"""
        return self.sqs.delete_message(receipt_handle)
    
    def extend_job_timeout(self, receipt_handle: str, additional_seconds: int = 300) -> bool:
        """Extend the processing timeout for a job"""
        return self.sqs.change_message_visibility(receipt_handle, additional_seconds)
