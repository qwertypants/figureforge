"""
API URL Configuration
"""

from django.urls import path
from api.views import (
    # Auth views
    auth,
    magic_link_auth,
    # Image views
    images,
    # Subscription views
    subscriptions,
    # Webhook views
    webhooks,
    # Pricing views
    pricing
)

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/user/', auth.get_current_user, name='get_current_user'),
    path('auth/user/update/', auth.update_user_profile, name='update_user_profile'),
    path('auth/user/stats/', auth.get_user_stats, name='get_user_stats'),
    path('auth/verify/', auth.verify_token, name='verify_token'),
    path('auth/delete/', auth.delete_account, name='delete_account'),
    
    # Magic link authentication
    path('auth/magic-link/request/', magic_link_auth.request_magic_link, name='request_magic_link'),
    path('auth/magic-link/verify/', magic_link_auth.verify_magic_link, name='verify_magic_link'),
    path('auth/magic-link/check-user/', magic_link_auth.check_magic_link_user, name='check_magic_link_user'),
    
    # Image generation endpoints
    path('images/generate/', images.generate_images, name='generate_images'),
    path('images/job/<str:job_id>/', images.get_job_status, name='get_job_status'),
    path('images/user/', images.get_user_images, name='get_user_images'),
    path('images/gallery/', images.get_public_gallery, name='get_public_gallery'),
    path('images/<str:image_id>/', images.get_image_details, name='get_image_details'),
    path('images/<str:image_id>/delete/', images.delete_image, name='delete_image'),
    path('images/<str:image_id>/update/', images.update_image_metadata, name='update_image_metadata'),
    path('images/<str:image_id>/favorite/', images.favorite_image, name='favorite_image'),
    path('images/models/', images.get_generation_models, name='get_generation_models'),
    
    # Pricing endpoints
    path('pricing/', pricing.get_pricing, name='get_pricing'),
    
    # Subscription endpoints
    path('subscriptions/plans/', subscriptions.get_subscription_plans, name='get_subscription_plans'),
    path('subscriptions/current/', subscriptions.get_current_subscription, name='get_current_subscription'),
    path('subscriptions/checkout/', subscriptions.create_checkout_session, name='create_checkout_session'),
    path('subscriptions/portal/', subscriptions.create_billing_portal_session, name='create_billing_portal_session'),
    path('subscriptions/cancel/', subscriptions.cancel_subscription, name='cancel_subscription'),
    path('subscriptions/reactivate/', subscriptions.reactivate_subscription, name='reactivate_subscription'),
    path('subscriptions/history/', subscriptions.get_billing_history, name='get_billing_history'),
    path('subscriptions/payment-method/', subscriptions.update_payment_method, name='update_payment_method'),
    
    # Webhook endpoints
    path('webhooks/stripe/', webhooks.stripe_webhook, name='stripe_webhook'),
    path('webhooks/health/', webhooks.webhook_health, name='webhook_health'),
]
