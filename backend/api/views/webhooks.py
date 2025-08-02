"""
Webhook handlers for external services
"""

import json
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt as django_csrf_exempt

from api.core.stripe_client import StripeWebhookHandler


@django_csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not sig_header:
        return Response(
            {'error': 'Missing Stripe signature header'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    webhook_handler = StripeWebhookHandler()
    
    try:
        result = webhook_handler.handle_webhook(payload, sig_header)
        
        return Response({
            'status': 'success',
            'result': result
        })
        
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Stripe webhook error: {str(e)}")
        
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_health(request):
    """Health check endpoint for webhooks"""
    return Response({
        'status': 'healthy',
        'service': 'webhooks'
    })
