#!/usr/bin/env python
"""
Test script to verify backend setup and configuration
"""

import os
import sys
import django

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'figureforge.settings')
django.setup()

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing imports...")
    
    try:
        from api.core import dynamodb_utils
        print("✓ DynamoDB utils imported successfully")
    except Exception as e:
        print(f"✗ Failed to import DynamoDB utils: {e}")
    
    try:
        from api.core import s3_utils
        print("✓ S3 utils imported successfully")
    except Exception as e:
        print(f"✗ Failed to import S3 utils: {e}")
    
    try:
        from api.core import sqs_utils
        print("✓ SQS utils imported successfully")
    except Exception as e:
        print(f"✗ Failed to import SQS utils: {e}")
    
    try:
        from api.core import fal_client
        print("✓ fal.ai client imported successfully")
    except Exception as e:
        print(f"✗ Failed to import fal.ai client: {e}")
    
    try:
        from api.core import stripe_client
        print("✓ Stripe client imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Stripe client: {e}")
    
    try:
        from api.middleware import cognito_auth
        print("✓ Cognito auth middleware imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Cognito auth: {e}")

def test_settings():
    """Test that required settings are configured"""
    print("\nTesting settings...")
    
    from django.conf import settings
    
    required_settings = [
        'SECRET_KEY',
        'AWS_REGION',
        'DYNAMODB_TABLE_NAME',
        'S3_BUCKET_NAME',
        'SQS_QUEUE_URL',
        'COGNITO_USER_POOL_ID',
        'COGNITO_APP_CLIENT_ID',
        'STRIPE_SECRET_KEY',
        'FAL_API_KEY'
    ]
    
    for setting in required_settings:
        if hasattr(settings, setting):
            value = getattr(settings, setting)
            if value and value != 'your-placeholder-value':
                print(f"✓ {setting} is configured")
            else:
                print(f"⚠ {setting} is set but appears to be a placeholder")
        else:
            print(f"✗ {setting} is not configured")

def test_urls():
    """Test that URLs are properly configured"""
    print("\nTesting URL configuration...")
    
    try:
        from django.urls import reverse
        
        # Test some key URLs
        test_urls = [
            ('api:get_current_user', 'auth/user/'),
            ('api:generate_images', 'images/generate/'),
            ('api:get_subscription_plans', 'subscriptions/plans/'),
            ('health_check', 'health/'),
        ]
        
        for url_name, expected_path in test_urls:
            try:
                url = reverse(url_name)
                print(f"✓ URL '{url_name}' resolves to {url}")
            except Exception as e:
                print(f"✗ Failed to resolve URL '{url_name}': {e}")
                
    except Exception as e:
        print(f"✗ Failed to test URLs: {e}")

def test_database():
    """Test database connectivity"""
    print("\nTesting database...")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")

def main():
    """Run all tests"""
    print("FigureForge Backend Setup Test")
    print("=" * 40)
    
    test_imports()
    test_settings()
    test_urls()
    test_database()
    
    print("\n" + "=" * 40)
    print("Setup test complete!")
    print("\nNote: Some tests may fail if environment variables are not configured.")
    print("Copy backend/.env.example to backend/.env and update with your values.")

if __name__ == '__main__':
    main()
