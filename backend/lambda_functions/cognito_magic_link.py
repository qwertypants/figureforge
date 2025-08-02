"""
Lambda functions for Cognito custom authentication flow (magic link)
"""

import json
import os
import secrets
import time
import boto3
from datetime import datetime, timedelta

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
cognito = boto3.client('cognito-idp')

# Environment variables
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'figureforge')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@figureforge.com')


def create_auth_challenge(event, context):
    """
    Create custom authentication challenge (send magic link)
    This Lambda is triggered during the authentication flow
    """
    email = event['request']['userAttributes']['email']
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    # Store token in DynamoDB with 15-minute expiration
    table = dynamodb.Table(DYNAMODB_TABLE)
    expires_at = int(time.time()) + 900  # 15 minutes
    
    table.put_item(
        Item={
            'PK': f'MAGIC_LINK#{email}',
            'SK': f'TOKEN#{token}',
            'email': email,
            'expires_at': expires_at,
            'created_at': int(time.time()),
            'used': False
        }
    )
    
    # Create magic link
    magic_link = f"{FRONTEND_URL}/auth/magic-link?token={token}&email={email}"
    
    # Send email
    try:
        ses.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Your FigureForge Sign In Link'},
                'Body': {
                    'Html': {
                        'Data': f"""
                        <html>
                            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                                <h2>Sign in to FigureForge</h2>
                                <p>Click the link below to sign in to your account:</p>
                                <p style="margin: 30px 0;">
                                    <a href="{magic_link}" 
                                       style="background-color: #4F46E5; color: white; padding: 12px 24px; 
                                              text-decoration: none; border-radius: 6px; display: inline-block;">
                                        Sign In to FigureForge
                                    </a>
                                </p>
                                <p>This link will expire in 15 minutes.</p>
                                <p style="color: #666; font-size: 14px;">
                                    If you didn't request this email, you can safely ignore it.
                                </p>
                            </body>
                        </html>
                        """
                    }
                }
            }
        )
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        # You might want to use SNS or another email service as fallback
    
    # Return the challenge metadata
    event['response']['publicChallengeParameters'] = {
        'email': email
    }
    event['response']['privateChallengeParameters'] = {
        'token': token
    }
    event['response']['challengeMetadata'] = 'MAGIC_LINK'
    
    return event


def verify_auth_challenge_response(event, context):
    """
    Verify the magic link token
    """
    expected_token = event['request']['privateChallengeParameters'].get('token', '')
    provided_token = event['request']['challengeAnswer']
    
    # Verify tokens match
    if expected_token == provided_token:
        # Verify token hasn't been used and isn't expired
        email = event['request']['userAttributes']['email']
        table = dynamodb.Table(DYNAMODB_TABLE)
        
        try:
            response = table.get_item(
                Key={
                    'PK': f'MAGIC_LINK#{email}',
                    'SK': f'TOKEN#{provided_token}'
                }
            )
            
            if 'Item' in response:
                item = response['Item']
                current_time = int(time.time())
                
                # Check if token is valid
                if not item.get('used', False) and item.get('expires_at', 0) > current_time:
                    # Mark token as used
                    table.update_item(
                        Key={
                            'PK': f'MAGIC_LINK#{email}',
                            'SK': f'TOKEN#{provided_token}'
                        },
                        UpdateExpression='SET used = :used',
                        ExpressionAttributeValues={':used': True}
                    )
                    
                    event['response']['answerCorrect'] = True
                else:
                    event['response']['answerCorrect'] = False
            else:
                event['response']['answerCorrect'] = False
                
        except Exception as e:
            print(f"Error verifying token: {str(e)}")
            event['response']['answerCorrect'] = False
    else:
        event['response']['answerCorrect'] = False
    
    return event


def define_auth_challenge(event, context):
    """
    Define which challenge to present to the user
    """
    # Check if this is the first auth attempt
    if len(event['request']['session']) == 0:
        # Start with SRP_A (required for custom auth flow)
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = False
        event['response']['challengeName'] = 'CUSTOM_CHALLENGE'
    elif len(event['request']['session']) == 1:
        # After SRP_A, issue our custom challenge
        event['response']['issueTokens'] = False
        event['response']['failAuthentication'] = False
        event['response']['challengeName'] = 'CUSTOM_CHALLENGE'
    else:
        # Check if the user successfully answered the challenge
        session = event['request']['session']
        if session[-1]['challengeName'] == 'CUSTOM_CHALLENGE' and session[-1]['challengeResult']:
            # Challenge answered correctly, issue tokens
            event['response']['issueTokens'] = True
            event['response']['failAuthentication'] = False
        else:
            # Challenge failed or too many attempts
            event['response']['issueTokens'] = False
            event['response']['failAuthentication'] = True
    
    return event


def pre_signup(event, context):
    """
    Auto-confirm users since we're using magic links
    """
    event['response']['autoConfirmUser'] = True
    event['response']['autoVerifyEmail'] = True
    return event