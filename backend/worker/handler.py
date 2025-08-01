"""
AWS Lambda handler for processing image generation jobs from SQS
"""

import json
import os
import sys
import time
import uuid
from typing import Dict, List, Any

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core.dynamodb_utils import JobRepository, ImageRepository, UserRepository
from api.core.s3_utils import ImageStorage
from api.core.fal_client import ImageGenerator


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process image generation jobs from SQS queue
    
    Args:
        event: SQS event containing job messages
        context: Lambda context
    
    Returns:
        Response with processing results
    """
    
    # Initialize repositories
    job_repo = JobRepository()
    image_repo = ImageRepository()
    user_repo = UserRepository()
    storage = ImageStorage()
    generator = ImageGenerator()
    
    processed_jobs = []
    failed_jobs = []
    
    # Process each message from SQS
    for record in event.get('Records', []):
        try:
            # Parse the message body
            message_body = json.loads(record['body'])
            job_data = message_body.get('job', {})
            
            if not job_data:
                print(f"Invalid message format: {record['body']}")
                continue
            
            job_id = job_data['job_id']
            user_id = job_data['user_id']
            
            print(f"Processing job {job_id} for user {user_id}")
            
            # Update job status to processing
            job_repo.update_job_status(user_id, job_id, 'processing')
            
            # Get user to check quota
            user = user_repo.get_user(user_id)
            if not user:
                raise Exception(f"User {user_id} not found")
            
            # Generate images
            filters = job_data.get('filters', {})
            batch_size = job_data.get('batch_size', 1)
            model_key = filters.pop('model', 'flux_dev')  # Extract model from filters
            
            generated_images = []
            total_cost = 0
            
            try:
                # Generate batch of images
                images = generator.generate_batch(
                    filters=filters,
                    batch_size=batch_size,
                    model_key=model_key
                )
                
                # Process each generated image
                for img_data in images:
                    # Download image from fal.ai URL
                    image_content = storage.download_image_from_url(img_data['url'])
                    
                    # Generate unique filename
                    image_id = str(uuid.uuid4())
                    filename = f"images/{user_id}/{image_id}.png"
                    
                    # Upload to S3
                    s3_url = storage.upload_image(image_content, filename)
                    
                    # Create image record in DynamoDB
                    image_record = image_repo.create_image(
                        user_id=user_id,
                        job_id=job_id,
                        url=s3_url,
                        prompt=img_data['prompt'],
                        model_id=img_data['model_id'],
                        model_name=img_data['model_name'],
                        parameters=img_data['parameters'],
                        seed=img_data.get('seed'),
                        tags=filters.get('tags', []),
                        public=filters.get('public', True)
                    )
                    
                    generated_images.append(image_record['image_id'])
                    total_cost += img_data['cost_cents']
                
                # Update job with completed status
                job_repo.update_job_status(
                    user_id=user_id,
                    job_id=job_id,
                    status='completed',
                    updates={
                        'image_ids': generated_images,
                        'total_cost_cents': total_cost,
                        'completed_at': int(time.time())
                    }
                )
                
                processed_jobs.append({
                    'job_id': job_id,
                    'user_id': user_id,
                    'images_generated': len(generated_images),
                    'total_cost_cents': total_cost
                })
                
                print(f"Successfully processed job {job_id}: {len(generated_images)} images")
                
            except Exception as e:
                # Handle generation failure
                error_message = str(e)
                print(f"Failed to generate images for job {job_id}: {error_message}")
                
                # Update job with failed status
                job_repo.update_job_status(
                    user_id=user_id,
                    job_id=job_id,
                    status='failed',
                    updates={
                        'error': error_message,
                        'failed_at': int(time.time())
                    }
                )
                
                # Refund quota on failure
                user_repo.update_user(user_id, {
                    'quota_used': max(0, user['quota_used'] - batch_size)
                })
                
                failed_jobs.append({
                    'job_id': job_id,
                    'user_id': user_id,
                    'error': error_message
                })
                
        except Exception as e:
            # Handle message processing failure
            print(f"Failed to process message: {str(e)}")
            failed_jobs.append({
                'message_id': record.get('messageId'),
                'error': str(e)
            })
    
    # Return processing results
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': len(processed_jobs),
            'failed': len(failed_jobs),
            'processed_jobs': processed_jobs,
            'failed_jobs': failed_jobs
        })
    }


def process_single_job(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single job (for testing purposes)
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        Processing result
    """
    
    # Create a fake SQS event
    event = {
        'Records': [{
            'body': json.dumps({'job': job_data}),
            'messageId': 'test-message'
        }]
    }
    
    # Process using the Lambda handler
    return lambda_handler(event, None)


if __name__ == '__main__':
    # Test the handler locally
    test_job = {
        'job_id': 'test-job-123',
        'user_id': 'test-user-123',
        'filters': {
            'body_type': 'athletic',
            'pose': 'standing',
            'lighting': 'natural',
            'model': 'flux_dev'
        },
        'batch_size': 1
    }
    
    result = process_single_job(test_job)
    print(json.dumps(result, indent=2))
