"""
Magic link authentication endpoints
"""

import boto3
import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings

# Validate required settings
if not settings.COGNITO_USER_POOL_ID:
    raise ValueError("COGNITO_USER_POOL_ID is not set in environment variables")
if not settings.COGNITO_CLIENT_ID:
    raise ValueError("COGNITO_CLIENT_ID is not set in environment variables")
if not settings.COGNITO_REGION:
    raise ValueError("COGNITO_REGION is not set in environment variables")

# Initialize Cognito client
cognito = boto3.client(
    'cognito-idp',
    region_name=settings.COGNITO_REGION
)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_magic_link(request):
    """
    Request a magic link to be sent to the user's email
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Generate a unique username based on email
        import uuid
        username = f"user_{uuid.uuid4().hex[:8]}"
        
        # Check if user exists by email
        try:
            # List users with the given email
            response = cognito.list_users(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Filter=f'email = "{email}"',
                Limit=1
            )
            
            if response['Users']:
                user_exists = True
                username = response['Users'][0]['Username']
            else:
                user_exists = False
                
        except Exception as e:
            print(f"Error checking user existence: {str(e)}")
            user_exists = False
        
        if not user_exists:
            # Create user account with temporary password
            # User will authenticate via magic link, so password won't be used
            import secrets
            temp_password = secrets.token_urlsafe(32)
            
            cognito.admin_create_user(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=username,  # Use generated username instead of email
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'true'}
                ],
                TemporaryPassword=temp_password,
                MessageAction='SUPPRESS'  # Don't send welcome email
            )
            
            # Set permanent password to allow custom auth
            cognito.admin_set_user_password(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=username,
                Password=temp_password,
                Permanent=True
            )
        
        # Initiate auth flow using email as the auth parameter
        auth_response = cognito.admin_initiate_auth(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            ClientId=settings.COGNITO_CLIENT_ID,
            AuthFlow='CUSTOM_AUTH',
            AuthParameters={
                'USERNAME': email  # Cognito will map this to the actual username via email alias
            }
        )
        
        return Response({
            'message': 'Magic link sent to your email',
            'session': auth_response.get('Session'),
            'email': email
        })
        
    except Exception as e:
        print(f"Magic link request error: {str(e)}")
        return Response(
            {'error': 'Failed to send magic link'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_magic_link(request):
    """
    Verify the magic link token and complete authentication
    """
    email = request.data.get('email')
    token = request.data.get('token')
    session = request.data.get('session')
    
    if not all([email, token, session]):
        return Response(
            {'error': 'Email, token, and session are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Respond to the auth challenge with the token
        auth_response = cognito.admin_respond_to_auth_challenge(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            ClientId=settings.COGNITO_CLIENT_ID,
            ChallengeName='CUSTOM_CHALLENGE',
            ChallengeResponses={
                'USERNAME': email,
                'ANSWER': token
            },
            Session=session
        )
        
        # If successful, we'll get tokens
        if 'AuthenticationResult' in auth_response:
            result = auth_response['AuthenticationResult']
            
            # Get user info from the ID token
            id_token = result['IdToken']
            
            return Response({
                'access_token': result['AccessToken'],
                'id_token': id_token,
                'refresh_token': result.get('RefreshToken'),
                'expires_in': result['ExpiresIn'],
                'token_type': result['TokenType']
            })
        else:
            return Response(
                {'error': 'Invalid or expired magic link'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except cognito.exceptions.NotAuthorizedException:
        return Response(
            {'error': 'Invalid or expired magic link'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        print(f"Magic link verification error: {str(e)}")
        return Response(
            {'error': 'Failed to verify magic link'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def check_magic_link_user(request):
    """
    Check if a user exists for magic link flow
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # List users with the given email
        response = cognito.list_users(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            Filter=f'email = "{email}"',
            Limit=1
        )
        
        if response['Users']:
            return Response({'exists': True})
        else:
            return Response({'exists': False})
            
    except Exception as e:
        print(f"User check error: {str(e)}")
        return Response(
            {'error': 'Failed to check user'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )