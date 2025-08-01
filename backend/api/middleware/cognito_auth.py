"""
Cognito JWT validation middleware for Django REST Framework
Validates JWT tokens from Amazon Cognito
"""

import json
import time
import urllib.request
from functools import lru_cache
from typing import Dict, Optional

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject
from jose import jwt, jwk, JWTError
from rest_framework import authentication, exceptions

from api.core.dynamodb_utils import UserRepository


class CognitoUser:
    """Custom user class for Cognito authenticated users"""
    
    def __init__(self, user_data: Dict):
        self.user_id = user_data.get('user_id')
        self.email = user_data.get('email')
        self.username = user_data.get('username')
        self.role = user_data.get('role', 'user')
        self.quota_used = user_data.get('quota_used', 0)
        self.quota_limit = user_data.get('quota_limit', 0)
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = True
        self.is_staff = self.role == 'admin'
        self.is_superuser = self.role == 'admin'
        self._user_data = user_data
    
    def __str__(self):
        return self.email or self.username or self.user_id
    
    @property
    def pk(self):
        return self.user_id
    
    def get_username(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        """Check if user has a specific permission"""
        if self.is_superuser:
            return True
        # Add custom permission logic here
        return False
    
    def has_perms(self, perm_list, obj=None):
        """Check if user has all permissions in list"""
        return all(self.has_perm(perm, obj) for perm in perm_list)
    
    def has_module_perms(self, app_label):
        """Check if user has permissions for app"""
        if self.is_superuser:
            return True
        return False


@lru_cache(maxsize=1)
def get_cognito_jwks() -> Dict:
    """Fetch and cache Cognito JWKS (JSON Web Key Set)"""
    jwks_url = f'https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json'
    
    try:
        with urllib.request.urlopen(jwks_url) as response:
            return json.loads(response.read())
    except Exception as e:
        raise Exception(f"Failed to fetch Cognito JWKS: {str(e)}")


def verify_cognito_token(token: str) -> Dict:
    """Verify and decode a Cognito JWT token"""
    # Get JWKS
    jwks = get_cognito_jwks()
    
    # Get the kid from the headers prior to verification
    try:
        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']
    except Exception:
        raise exceptions.AuthenticationFailed('Invalid token format')
    
    # Search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(jwks['keys'])):
        if kid == jwks['keys'][i]['kid']:
            key_index = i
            break
    
    if key_index == -1:
        raise exceptions.AuthenticationFailed('Public key not found in JWKS')
    
    # Construct the public key
    public_key = jwk.construct(jwks['keys'][key_index])
    
    # Verify the token
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=settings.COGNITO_CLIENT_ID,
            issuer=f'https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}'
        )
    except JWTError as e:
        raise exceptions.AuthenticationFailed(f'Token verification failed: {str(e)}')
    
    # Verify token expiration
    if payload.get('exp', 0) < time.time():
        raise exceptions.AuthenticationFailed('Token has expired')
    
    return payload


class CognitoAuthentication(authentication.BaseAuthentication):
    """DRF Authentication class for Cognito JWT tokens"""
    
    def authenticate(self, request):
        """Authenticate the request and return a tuple of (user, token)"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            # Verify the token
            payload = verify_cognito_token(token)
            
            # Extract user information
            cognito_user_id = payload.get('sub')
            email = payload.get('email')
            
            if not cognito_user_id:
                raise exceptions.AuthenticationFailed('Invalid token payload')
            
            # Get or create user in DynamoDB
            user_repo = UserRepository()
            user_data = user_repo.get_user(cognito_user_id)
            
            if not user_data:
                # Create new user
                user_data = user_repo.create_user(
                    user_id=cognito_user_id,
                    email=email
                )
            
            # Create CognitoUser instance
            user = CognitoUser(user_data)
            
            return (user, token)
            
        except exceptions.AuthenticationFailed:
            raise
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def authenticate_header(self, request):
        """Return the WWW-Authenticate header"""
        return 'Bearer'


class CognitoAuthMiddleware:
    """Middleware to add Cognito user to request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: self.get_user(request))
        response = self.get_response(request)
        return response
    
    def get_user(self, request):
        """Get user from request"""
        # Try to authenticate using CognitoAuthentication
        auth = CognitoAuthentication()
        try:
            user_auth_tuple = auth.authenticate(request)
            if user_auth_tuple:
                return user_auth_tuple[0]
        except:
            pass
        
        return AnonymousUser()


def cognito_permission_required(permission: str):
    """Decorator to check if user has specific permission"""
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                raise exceptions.NotAuthenticated()
            
            if not request.user.has_perm(permission):
                raise exceptions.PermissionDenied()
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def admin_required(view_func):
    """Decorator to check if user is admin"""
    def wrapped_view(request, *args, **kwargs):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            raise exceptions.NotAuthenticated()
        
        if not request.user.is_staff:
            raise exceptions.PermissionDenied('Admin access required')
        
        return view_func(request, *args, **kwargs)
    return wrapped_view
