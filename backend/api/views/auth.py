"""
Authentication and user management views
"""

import time
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from api.core.dynamodb_utils import UserRepository
from api.middleware.cognito_auth import CognitoAuthentication


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user details"""
    user = request.user
    
    return Response({
        'user_id': user.user_id,
        'email': user.email,
        'username': user.username,
        'role': user.role,
        'quota_used': user.quota_used,
        'quota_limit': user.quota_limit,
        'subscription_plan': getattr(user, 'subscription_plan', None)
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update user profile information"""
    user_repo = UserRepository()
    
    # Only allow updating certain fields
    allowed_fields = ['username', 'preferences']
    updates = {}
    
    for field in allowed_fields:
        if field in request.data:
            updates[field] = request.data[field]
    
    if not updates:
        return Response(
            {'error': 'No valid fields to update'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        updated_user = user_repo.update_user(request.user.user_id, updates)
        
        return Response({
            'message': 'Profile updated successfully',
            'user': {
                'user_id': updated_user['user_id'],
                'email': updated_user['email'],
                'username': updated_user['username']
            }
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """Get user statistics and usage"""
    user = request.user
    
    # Calculate usage percentage
    usage_percentage = 0
    if user.quota_limit > 0:
        usage_percentage = (user.quota_used / user.quota_limit) * 100
    
    return Response({
        'quota_used': user.quota_used,
        'quota_limit': user.quota_limit,
        'usage_percentage': round(usage_percentage, 2),
        'images_remaining': max(0, user.quota_limit - user.quota_used),
        'subscription_plan': getattr(user, 'subscription_plan', 'free')
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
    """Verify a Cognito JWT token"""
    token = request.data.get('token')
    
    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Use CognitoAuthentication to verify token
        auth = CognitoAuthentication()
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        user_auth_tuple = auth.authenticate(request)
        
        if user_auth_tuple:
            user = user_auth_tuple[0]
            return Response({
                'valid': True,
                'user': {
                    'user_id': user.user_id,
                    'email': user.email,
                    'username': user.username
                }
            })
        else:
            return Response({
                'valid': False,
                'error': 'Invalid token'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({
            'valid': False,
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Delete user account (soft delete)"""
    user_repo = UserRepository()
    
    # Confirm deletion with a required field
    if not request.data.get('confirm_delete'):
        return Response(
            {'error': 'Please confirm account deletion'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Soft delete the user
        user_repo.update_user(request.user.user_id, {
            'deleted_at': int(time.time()),
            'status': 'deleted'
        })
        
        return Response({
            'message': 'Account deleted successfully'
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
