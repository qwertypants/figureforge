"""
DynamoDB utilities for single-table design
Handles CRUD operations for all entities in the FigureForge application
"""

import boto3
import uuid
import time
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from django.conf import settings
from botocore.exceptions import ClientError


class DynamoDBClient:
    """Wrapper for DynamoDB operations with single-table design"""
    
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.table = self.dynamodb.Table(settings.AWS_DYNAMODB_TABLE_NAME)
    
    def _serialize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python types to DynamoDB-compatible types"""
        serialized = {}
        for key, value in item.items():
            if isinstance(value, float):
                serialized[key] = Decimal(str(value))
            elif isinstance(value, list):
                serialized_list = []
                for v in value:
                    if isinstance(v, float):
                        serialized_list.append(Decimal(str(v)))
                    elif isinstance(v, dict):
                        serialized_list.append(self._serialize_item(v))
                    else:
                        serialized_list.append(v)
                serialized[key] = serialized_list
            elif isinstance(value, dict):
                serialized[key] = self._serialize_item(value)
            else:
                serialized[key] = value
        return serialized
    
    def _deserialize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB types back to Python types"""
        deserialized = {}
        for key, value in item.items():
            if isinstance(value, Decimal):
                deserialized[key] = float(value)
            elif isinstance(value, list):
                deserialized_list = []
                for v in value:
                    if isinstance(v, Decimal):
                        deserialized_list.append(float(v))
                    elif isinstance(v, dict):
                        deserialized_list.append(self._deserialize_item(v))
                    else:
                        deserialized_list.append(v)
                deserialized[key] = deserialized_list
            elif isinstance(value, dict):
                deserialized[key] = self._deserialize_item(value)
            else:
                deserialized[key] = value
        return deserialized
    
    def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update an item"""
        # Add timestamp if not present
        if 'created_at' not in item:
            item['created_at'] = int(time.time())
        
        serialized_item = self._serialize_item(item)
        
        try:
            self.table.put_item(Item=serialized_item)
            return self._deserialize_item(serialized_item)
        except ClientError as e:
            raise Exception(f"Error putting item: {e.response['Error']['Message']}")
    
    def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """Get a single item by primary key"""
        try:
            response = self.table.get_item(
                Key={'pk': pk, 'sk': sk}
            )
            if 'Item' in response:
                return self._deserialize_item(response['Item'])
            return None
        except ClientError as e:
            raise Exception(f"Error getting item: {e.response['Error']['Message']}")
    
    def query_items(self, pk: str, sk_prefix: Optional[str] = None, 
                   limit: Optional[int] = None, last_evaluated_key: Optional[Dict] = None) -> Tuple[List[Dict[str, Any]], Optional[Dict]]:
        """Query items by partition key and optional sort key prefix"""
        query_params = {
            'KeyConditionExpression': 'pk = :pk',
            'ExpressionAttributeValues': {':pk': pk}
        }
        
        if sk_prefix:
            query_params['KeyConditionExpression'] += ' AND begins_with(sk, :sk_prefix)'
            query_params['ExpressionAttributeValues'][':sk_prefix'] = sk_prefix
        
        if limit:
            query_params['Limit'] = limit
        
        if last_evaluated_key:
            query_params['ExclusiveStartKey'] = last_evaluated_key
        
        try:
            response = self.table.query(**query_params)
            items = [self._deserialize_item(item) for item in response.get('Items', [])]
            return items, response.get('LastEvaluatedKey')
        except ClientError as e:
            raise Exception(f"Error querying items: {e.response['Error']['Message']}")
    
    def delete_item(self, pk: str, sk: str) -> bool:
        """Delete an item (soft delete by setting deleted_at)"""
        try:
            self.table.update_item(
                Key={'pk': pk, 'sk': sk},
                UpdateExpression='SET deleted_at = :timestamp',
                ExpressionAttributeValues={':timestamp': int(time.time())}
            )
            return True
        except ClientError as e:
            raise Exception(f"Error deleting item: {e.response['Error']['Message']}")
    
    def query_gsi(self, index_name: str, pk_value: str, sk_value: Optional[str] = None,
                  limit: Optional[int] = None, last_evaluated_key: Optional[Dict] = None) -> Tuple[List[Dict[str, Any]], Optional[Dict]]:
        """Query a Global Secondary Index"""
        query_params = {
            'IndexName': index_name,
            'KeyConditionExpression': 'pk = :pk',
            'ExpressionAttributeValues': {':pk': pk_value}
        }
        
        if sk_value:
            query_params['KeyConditionExpression'] += ' AND sk = :sk'
            query_params['ExpressionAttributeValues'][':sk'] = sk_value
        
        if limit:
            query_params['Limit'] = limit
        
        if last_evaluated_key:
            query_params['ExclusiveStartKey'] = last_evaluated_key
        
        try:
            response = self.table.query(**query_params)
            items = [self._deserialize_item(item) for item in response.get('Items', [])]
            return items, response.get('LastEvaluatedKey')
        except ClientError as e:
            raise Exception(f"Error querying GSI: {e.response['Error']['Message']}")


class UserRepository:
    """Repository for User entity operations"""
    
    def __init__(self):
        self.db = DynamoDBClient()
    
    def create_user(self, user_id: str, email: str, username: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user"""
        user = {
            'pk': f'USER#{user_id}',
            'sk': 'PROFILE',
            'user_id': user_id,
            'email': email,
            'username': username or f'user_{user_id[:8]}',
            'role': 'user',
            'quota_used': 0,
            'quota_limit': 0,  # Will be set based on subscription
            'created_at': int(time.time())
        }
        
        # Also create email index entry
        email_index = {
            'pk': f'EMAIL#{email}',
            'sk': f'USER#{user_id}',
            'created_at': int(time.time())
        }
        
        self.db.put_item(user)
        self.db.put_item(email_index)
        
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.db.get_item(f'USER#{user_id}', 'PROFILE')
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email using GSI"""
        items, _ = self.db.query_gsi('byEmail', f'EMAIL#{email}', limit=1)
        if items:
            user_id = items[0]['sk'].split('#')[1]
            return self.get_user(user_id)
        return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.update(updates)
        return self.db.put_item(user)


class ImageRepository:
    """Repository for Image entity operations"""
    
    def __init__(self):
        self.db = DynamoDBClient()
    
    def create_image(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new image record"""
        image_id = str(uuid.uuid4())
        image = {
            'pk': f'IMG#{image_id}',
            'sk': 'META',
            'image_id': image_id,
            'user_id': image_data.get('user_id'),
            'url': image_data['url'],
            'tags': image_data.get('tags', []),
            'prompt_json': image_data.get('prompt_json', {}),
            'provider': image_data.get('provider', 'fal.ai'),
            'provider_model_id': image_data.get('provider_model_id'),
            'cost_cents': image_data.get('cost_cents', 0),
            'favorited_count': 0,
            'public': image_data.get('public', True),
            'private_gallery_ids': image_data.get('private_gallery_ids', []),
            'flag_status': 'clean',
            'created_at': int(time.time()),
            'deleted_at': None
        }
        
        self.db.put_item(image)
        
        # Create tag index entries
        for tag in image['tags']:
            tag_index = {
                'pk': f'TAG#{tag}',
                'sk': f'IMG#{image_id}',
                'created_at': int(time.time())
            }
            self.db.put_item(tag_index)
        
        # Create user image index entry if user_id exists
        if image['user_id']:
            user_image_index = {
                'pk': f'USER#{image['user_id']}',
                'sk': f'IMG#{image_id}',
                'created_at': int(time.time())
            }
            self.db.put_item(user_image_index)
        
        return image
    
    def get_image(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get image by ID"""
        return self.db.get_item(f'IMG#{image_id}', 'META')
    
    def get_images_by_tag(self, tag: str, limit: int = 20, cursor: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Get images by tag"""
        last_key = {'pk': f'TAG#{tag}', 'sk': cursor} if cursor else None
        
        items, next_key = self.db.query_items(f'TAG#{tag}', limit=limit, last_evaluated_key=last_key)
        
        # Fetch full image data
        images = []
        for item in items:
            image_id = item['sk'].split('#')[1]
            image = self.get_image(image_id)
            if image and not image.get('deleted_at'):
                images.append(image)
        
        next_cursor = next_key['sk'] if next_key else None
        return images, next_cursor
    
    def get_user_images(self, user_id: str, limit: int = 20, cursor: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Get images by user"""
        last_key = {'pk': f'USER#{user_id}', 'sk': cursor} if cursor else None
        
        items, next_key = self.db.query_gsi('imagesByUser', f'USER#{user_id}', limit=limit, last_evaluated_key=last_key)
        
        # Fetch full image data
        images = []
        for item in items:
            if item['sk'].startswith('IMG#'):
                image_id = item['sk'].split('#')[1]
                image = self.get_image(image_id)
                if image and not image.get('deleted_at'):
                    images.append(image)
        
        next_cursor = next_key['sk'] if next_key else None
        return images, next_cursor


class JobRepository:
    """Repository for GenerationJob entity operations"""
    
    def __init__(self):
        self.db = DynamoDBClient()
    
    def create_job(self, user_id: str, filters: Dict[str, Any], batch_size: int) -> Dict[str, Any]:
        """Create a new generation job"""
        job_id = str(uuid.uuid4())
        job = {
            'pk': f'USER#{user_id}',
            'sk': f'JOB#{job_id}',
            'job_id': job_id,
            'user_id': user_id,
            'status': 'queued',
            'filters': filters,
            'batch_size': batch_size,
            'image_ids': [],
            'error': None,
            'created_at': int(time.time()),
            'updated_at': int(time.time())
        }
        
        self.db.put_item(job)
        
        # Also create job status index entry
        status_index = {
            'pk': f'JOBSTATUS#{job["status"]}',
            'sk': str(job['created_at']),
            'job_id': job_id,
            'user_id': user_id
        }
        self.db.put_item(status_index)
        
        return job
    
    def get_job(self, user_id: str, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        return self.db.get_item(f'USER#{user_id}', f'JOB#{job_id}')
    
    def update_job_status(self, user_id: str, job_id: str, status: str, 
                         image_ids: Optional[List[str]] = None, error: Optional[str] = None) -> Dict[str, Any]:
        """Update job status"""
        job = self.get_job(user_id, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Remove old status index entry
        old_status_index = {
            'pk': f'JOBSTATUS#{job["status"]}',
            'sk': str(job['created_at'])
        }
        self.db.delete_item(old_status_index['pk'], old_status_index['sk'])
        
        # Update job
        job['status'] = status
        job['updated_at'] = int(time.time())
        if image_ids:
            job['image_ids'] = image_ids
        if error:
            job['error'] = error
        
        self.db.put_item(job)
        
        # Create new status index entry
        new_status_index = {
            'pk': f'JOBSTATUS#{status}',
            'sk': str(job['created_at']),
            'job_id': job_id,
            'user_id': user_id
        }
        self.db.put_item(new_status_index)
        
        return job


class SubscriptionRepository:
    """Repository for Subscription entity operations"""
    
    def __init__(self):
        self.db = DynamoDBClient()
    
    def create_subscription(self, user_id: str, stripe_sub_id: str, plan_id: str, 
                          status: str, current_period_end: int) -> Dict[str, Any]:
        """Create a new subscription"""
        subscription = {
            'pk': f'USER#{user_id}',
            'sk': f'SUB#{stripe_sub_id}',
            'subscription_id': stripe_sub_id,
            'user_id': user_id,
            'plan_id': plan_id,
            'status': status,
            'current_period_end': current_period_end,
            'created_at': int(time.time()),
            'updated_at': int(time.time())
        }
        
        self.db.put_item(subscription)
        
        # Also create Stripe subscription index
        stripe_index = {
            'pk': f'SUB#{stripe_sub_id}',
            'sk': f'USER#{user_id}',
            'created_at': int(time.time())
        }
        self.db.put_item(stripe_index)
        
        return subscription
    
    def get_subscription(self, user_id: str, stripe_sub_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription by ID"""
        return self.db.get_item(f'USER#{user_id}', f'SUB#{stripe_sub_id}')
    
    def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all subscriptions for a user"""
        items, _ = self.db.query_items(f'USER#{user_id}', sk_prefix='SUB#')
        return [item for item in items if item.get('subscription_id')]
    
    def get_active_subscription(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get the active subscription for a user"""
        subscriptions = self.get_user_subscriptions(user_id)
        active_subs = [s for s in subscriptions if s['status'] == 'active']
        return active_subs[0] if active_subs else None
    
    def update_subscription(self, user_id: str, stripe_sub_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update subscription"""
        subscription = self.get_subscription(user_id, stripe_sub_id)
        if not subscription:
            raise ValueError(f"Subscription {stripe_sub_id} not found")
        
        subscription.update(updates)
        subscription['updated_at'] = int(time.time())
        
        return self.db.put_item(subscription)
