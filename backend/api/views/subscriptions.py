"""
Subscription management views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from api.core.stripe_client import StripeClient
from api.core.dynamodb_utils import SubscriptionRepository


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_plans(request):
    """Get available subscription plans"""
    stripe_client = StripeClient()
    
    plans = []
    for key, plan in stripe_client.plans.items():
        plans.append({
            'key': key,
            'name': plan['name'],
            'price_cents': plan['price_cents'],
            'price_display': f'${plan["price_cents"] / 100:.2f}/month',
            'quota': plan['quota'],
            'features': plan['features']
        })
    
    return Response({
        'plans': plans,
        'current_plan': getattr(request.user, 'subscription_plan', None)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_subscription(request):
    """Get current user's subscription details"""
    subscription_repo = SubscriptionRepository()
    
    try:
        # Get active subscription
        subscription = subscription_repo.get_active_subscription(request.user.user_id)
        
        if not subscription:
            return Response({
                'has_subscription': False,
                'plan': None,
                'status': 'none'
            })
        
        # Get plan details
        stripe_client = StripeClient()
        plan = stripe_client.plans.get(subscription['plan_id'])
        
        return Response({
            'has_subscription': True,
            'subscription_id': subscription['subscription_id'],
            'plan': {
                'key': subscription['plan_id'],
                'name': plan['name'] if plan else 'Unknown',
                'price_display': f'${plan["price_cents"] / 100:.2f}/month' if plan else 'N/A',
                'quota': plan['quota'] if plan else 0
            },
            'status': subscription['status'],
            'current_period_end': subscription['current_period_end'],
            'cancel_at_period_end': subscription.get('cancel_at_period_end', False)
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """Create a Stripe checkout session for subscription"""
    plan_key = request.data.get('plan')
    
    if not plan_key:
        return Response(
            {'error': 'Plan is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    stripe_client = StripeClient()
    
    # Validate plan
    if plan_key not in stripe_client.plans:
        return Response(
            {'error': 'Invalid plan'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Build success and cancel URLs
    frontend_url = request.data.get('frontend_url', 'http://localhost:5173')
    success_url = f"{frontend_url}/billing?session_id={{CHECKOUT_SESSION_ID}}&success=true"
    cancel_url = f"{frontend_url}/billing?canceled=true"
    
    try:
        checkout_url = stripe_client.create_checkout_session(
            user_id=request.user.user_id,
            plan_key=plan_key,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return Response({
            'checkout_url': checkout_url
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_billing_portal_session(request):
    """Create a Stripe billing portal session"""
    # Build return URL
    frontend_url = request.data.get('frontend_url', 'http://localhost:5173')
    return_url = f"{frontend_url}/billing"
    
    stripe_client = StripeClient()
    
    try:
        portal_url = stripe_client.create_billing_portal_session(
            user_id=request.user.user_id,
            return_url=return_url
        )
        
        return Response({
            'portal_url': portal_url
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancel the current subscription"""
    subscription_repo = SubscriptionRepository()
    stripe_client = StripeClient()
    
    # Get active subscription
    subscription = subscription_repo.get_active_subscription(request.user.user_id)
    
    if not subscription:
        return Response(
            {'error': 'No active subscription found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if immediate cancellation is requested
    immediate = request.data.get('immediate', False)
    
    try:
        result = stripe_client.cancel_subscription(
            user_id=request.user.user_id,
            subscription_id=subscription['subscription_id'],
            at_period_end=not immediate
        )
        
        return Response({
            'message': 'Subscription cancelled successfully',
            'cancel_at_period_end': result['cancel_at_period_end'],
            'current_period_end': result['current_period_end']
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reactivate_subscription(request):
    """Reactivate a cancelled subscription (before period end)"""
    subscription_repo = SubscriptionRepository()
    stripe_client = StripeClient()
    
    # Get active subscription
    subscription = subscription_repo.get_active_subscription(request.user.user_id)
    
    if not subscription:
        return Response(
            {'error': 'No active subscription found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not subscription.get('cancel_at_period_end'):
        return Response(
            {'error': 'Subscription is not scheduled for cancellation'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Reactivate by removing cancellation
        import stripe
        stripe_subscription = stripe.Subscription.modify(
            subscription['subscription_id'],
            cancel_at_period_end=False
        )
        
        # Update in database
        subscription_repo.update_subscription(
            request.user.user_id,
            subscription['subscription_id'],
            {'cancel_at_period_end': False}
        )
        
        return Response({
            'message': 'Subscription reactivated successfully',
            'status': stripe_subscription.status
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_billing_history(request):
    """Get user's billing history"""
    # This would need to fetch invoices from Stripe
    # For now, return not implemented
    return Response(
        {'error': 'Billing history not yet implemented'},
        status=status.HTTP_501_NOT_IMPLEMENTED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_payment_method(request):
    """Update payment method"""
    # This would redirect to Stripe billing portal
    # For now, return instruction to use billing portal
    return Response({
        'message': 'Please use the billing portal to update your payment method',
        'action': 'create_billing_portal_session'
    })
