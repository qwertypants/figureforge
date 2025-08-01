"""
Image generation and management views
"""

import json
import time
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings

from api.core.dynamodb_utils import ImageRepository, JobRepository, UserRepository
from api.core.sqs_utils import JobQueue
from api.core.s3_utils import ImageStorage
from api.core.fal_client import ImageGenerator


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_images(request):
    """Create a new image generation job"""
    user = request.user
    
    # Check quota
    if user.quota_used >= user.quota_limit:
        return Response(
            {'error': 'Quota exceeded. Please upgrade your subscription.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Validate request data
    filters = request.data.get('filters', {})
    batch_size = request.data.get('batch_size', 1)
    
    # Validate batch size
    if batch_size < 1 or batch_size > settings.MAX_BATCH_SIZE:
        return Response(
            {'error': f'Batch size must be between 1 and {settings.MAX_BATCH_SIZE}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if batch would exceed quota
    if user.quota_used + batch_size > user.quota_limit:
        available = user.quota_limit - user.quota_used
        return Response(
            {'error': f'Batch size exceeds available quota. You can generate up to {available} images.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Create job record
        job_repo = JobRepository()
        job = job_repo.create_job(
            user_id=user.user_id,
            filters=filters,
            batch_size=batch_size
        )
        
        # Queue job for processing
        queue = JobQueue()
        queue.enqueue_generation_job(job)
        
        # Update user quota (will be adjusted if job fails)
        user_repo = UserRepository()
        user_repo.update_user(user.user_id, {
            'quota_used': user.quota_used + batch_size
        })
        
        return Response({
            'job_id': job['job_id'],
            'status': job['status'],
            'batch_size': batch_size,
            'message': 'Image generation job queued successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_status(request, job_id):
    """Get the status of a generation job"""
    job_repo = JobRepository()
    
    try:
        job = job_repo.get_job(request.user.user_id, job_id)
        
        if not job:
            return Response(
                {'error': 'Job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get image details if job is completed
        images = []
        if job['status'] == 'completed' and job.get('image_ids'):
            image_repo = ImageRepository()
            storage = ImageStorage()
            
            for image_id in job['image_ids']:
                image = image_repo.get_image(image_id)
                if image:
                    # Generate signed URL
                    image['url'] = storage.get_signed_url(image['url'])
                    images.append(image)
        
        return Response({
            'job_id': job['job_id'],
            'status': job['status'],
            'batch_size': job['batch_size'],
            'created_at': job['created_at'],
            'updated_at': job['updated_at'],
            'error': job.get('error'),
            'images': images
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_images(request):
    """Get images created by the authenticated user"""
    image_repo = ImageRepository()
    storage = ImageStorage()
    
    # Pagination parameters
    limit = int(request.GET.get('limit', 20))
    cursor = request.GET.get('cursor')
    
    try:
        images, next_cursor = image_repo.get_user_images(
            user_id=request.user.user_id,
            limit=limit,
            cursor=cursor
        )
        
        # Generate signed URLs for images
        for image in images:
            image['url'] = storage.get_signed_url(image['url'])
        
        return Response({
            'images': images,
            'next_cursor': next_cursor,
            'has_more': next_cursor is not None
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_gallery(request):
    """Get public gallery images"""
    image_repo = ImageRepository()
    storage = ImageStorage()
    
    # Get filter parameters
    tag = request.GET.get('tag')
    limit = int(request.GET.get('limit', 20))
    cursor = request.GET.get('cursor')
    
    try:
        if tag:
            # Get images by tag
            images, next_cursor = image_repo.get_images_by_tag(
                tag=tag,
                limit=limit,
                cursor=cursor
            )
        else:
            # Get recent public images (would need to implement this method)
            return Response({
                'error': 'Gallery browsing without tags not yet implemented'
            }, status=status.HTTP_501_NOT_IMPLEMENTED)
        
        # Filter out private images and generate signed URLs
        public_images = []
        for image in images:
            if image.get('public', True):
                image['url'] = storage.get_signed_url(image['url'])
                # Remove sensitive data
                image.pop('user_id', None)
                public_images.append(image)
        
        return Response({
            'images': public_images,
            'next_cursor': next_cursor,
            'has_more': next_cursor is not None
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_image_details(request, image_id):
    """Get details for a specific image"""
    image_repo = ImageRepository()
    storage = ImageStorage()
    
    try:
        image = image_repo.get_image(image_id)
        
        if not image:
            return Response(
                {'error': 'Image not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check access permissions
        if not image.get('public', True) and image.get('user_id') != request.user.user_id:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate signed URL
        image['url'] = storage.get_signed_url(image['url'])
        
        # Remove sensitive data if not owner
        if image.get('user_id') != request.user.user_id:
            image.pop('user_id', None)
        
        return Response(image)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_image(request, image_id):
    """Delete an image (soft delete)"""
    image_repo = ImageRepository()
    
    try:
        image = image_repo.get_image(image_id)
        
        if not image:
            return Response(
                {'error': 'Image not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check ownership
        if image.get('user_id') != request.user.user_id:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete
        image_repo.db.delete_item(f'IMG#{image_id}', 'META')
        
        return Response({
            'message': 'Image deleted successfully'
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_image_metadata(request, image_id):
    """Update image metadata (tags, visibility, etc.)"""
    image_repo = ImageRepository()
    
    try:
        image = image_repo.get_image(image_id)
        
        if not image:
            return Response(
                {'error': 'Image not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check ownership
        if image.get('user_id') != request.user.user_id:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update allowed fields
        allowed_fields = ['tags', 'public', 'private_gallery_ids']
        updates = {}
        
        for field in allowed_fields:
            if field in request.data:
                updates[field] = request.data[field]
        
        if not updates:
            return Response(
                {'error': 'No valid fields to update'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update image
        image.update(updates)
        image_repo.db.put_item(image)
        
        # Update tag indices if tags changed
        if 'tags' in updates:
            # Remove old tag indices (simplified - in production would track old tags)
            # Add new tag indices
            for tag in updates['tags']:
                tag_index = {
                    'pk': f'TAG#{tag}',
                    'sk': f'IMG#{image_id}',
                    'created_at': int(time.time())
                }
                image_repo.db.put_item(tag_index)
        
        return Response({
            'message': 'Image updated successfully',
            'image': image
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def favorite_image(request, image_id):
    """Add/remove image from favorites"""
    # This would need a favorites tracking system in DynamoDB
    # For now, return not implemented
    return Response(
        {'error': 'Favorites feature not yet implemented'},
        status=status.HTTP_501_NOT_IMPLEMENTED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_generation_models(request):
    """Get available image generation models"""
    generator = ImageGenerator()
    
    models = []
    for key, config in generator.models.items():
        models.append({
            'key': key,
            'id': config['id'],
            'name': config['name'],
            'cost_cents': config['cost_cents'],
            'cost_display': f'${config["cost_cents"] / 100:.2f}'
        })
    
    return Response({
        'models': models,
        'default': 'flux_dev'
    })
