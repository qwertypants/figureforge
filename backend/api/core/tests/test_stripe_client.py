"""
Test cases for Stripe client and webhook handler
"""

from django.conf import settings

# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        AWS_REGION='us-east-1',
        AWS_ACCESS_KEY_ID='test-key-id',
        AWS_SECRET_ACCESS_KEY='test-secret-key',
        AWS_DYNAMODB_TABLE_NAME='test-table',
        STRIPE_SECRET_KEY='sk_test_dummy',
        STRIPE_WEBHOOK_SECRET='whsec_test_dummy',
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'api',
        ],
        USE_TZ=True,
    )

import pytest
import stripe
import time
import json
from unittest.mock import Mock, patch, MagicMock

from api.core.stripe_client import StripeClient, StripeWebhookHandler


class TestStripeClient:
    """Test cases for StripeClient class"""
    
    @pytest.fixture
    def mock_repos(self):
        """Mock repository dependencies"""
        mock_sub_repo = Mock()
        mock_user_repo = Mock()
        return mock_sub_repo, mock_user_repo
    
    @pytest.fixture
    def client(self, mock_repos):
        """Create StripeClient instance with mocked dependencies"""
        mock_sub_repo, mock_user_repo = mock_repos
        with patch('api.core.stripe_client.SubscriptionRepository', return_value=mock_sub_repo), \
             patch('api.core.stripe_client.UserRepository', return_value=mock_user_repo), \
             patch('api.core.stripe_client.settings') as mock_settings:
            mock_settings.STRIPE_SECRET_KEY = 'sk_test_123'
            client = StripeClient()
            client.subscription_repo = mock_sub_repo
            client.user_repo = mock_user_repo
            return client
    
    def test_init_sets_repositories_and_plans(self, client):
        """Test client initialization"""
        assert client.subscription_repo is not None
        assert client.user_repo is not None
        assert 'hobby' in client.plans
        assert 'pro' in client.plans
        assert 'studio' in client.plans
        
        # Check plan structure
        hobby_plan = client.plans['hobby']
        assert hobby_plan['price_cents'] == 999
        assert hobby_plan['quota'] == 100
        assert len(hobby_plan['features']) > 0
    
    @patch('stripe.Customer.create')
    def test_create_customer_success(self, mock_create, client):
        """Test successful customer creation"""
        mock_create.return_value = Mock(id='cus_123456')
        client.user_repo.update_user = Mock()
        
        customer_id = client.create_customer('user123', 'test@example.com')
        
        assert customer_id == 'cus_123456'
        
        mock_create.assert_called_once_with(
            email='test@example.com',
            metadata={'user_id': 'user123'}
        )
        
        client.user_repo.update_user.assert_called_once_with(
            'user123',
            {'stripe_customer_id': 'cus_123456'}
        )
    
    @patch('stripe.Customer.create')
    def test_create_customer_stripe_error(self, mock_create, client):
        """Test handling Stripe errors during customer creation"""
        mock_create.side_effect = stripe.error.StripeError('Test error')
        
        with pytest.raises(Exception) as exc_info:
            client.create_customer('user123', 'test@example.com')
        
        assert 'Failed to create Stripe customer' in str(exc_info.value)
    
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_new_customer(self, mock_session_create, client):
        """Test creating checkout session for new customer"""
        # Mock user without Stripe customer
        client.user_repo.get_user.return_value = {
            'user_id': 'user123',
            'email': 'test@example.com'
        }
        
        # Mock customer creation
        with patch.object(client, 'create_customer', return_value='cus_new123'):
            mock_session_create.return_value = Mock(url='https://checkout.stripe.com/session123')
            
            url = client.create_checkout_session(
                'user123',
                'hobby',
                'https://example.com/success',
                'https://example.com/cancel'
            )
        
        assert url == 'https://checkout.stripe.com/session123'
        
        mock_session_create.assert_called_once()
        call_args = mock_session_create.call_args[1]
        assert call_args['customer'] == 'cus_new123'
        assert call_args['mode'] == 'subscription'
        assert call_args['line_items'][0]['price'] == 'price_hobby'
        assert call_args['metadata']['user_id'] == 'user123'
        assert call_args['metadata']['plan_key'] == 'hobby'
    
    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session_existing_customer(self, mock_session_create, client):
        """Test creating checkout session for existing customer"""
        # Mock user with Stripe customer
        client.user_repo.get_user.return_value = {
            'user_id': 'user123',
            'email': 'test@example.com',
            'stripe_customer_id': 'cus_existing123'
        }
        
        mock_session_create.return_value = Mock(url='https://checkout.stripe.com/session456')
        
        url = client.create_checkout_session(
            'user123',
            'pro',
            'https://example.com/success',
            'https://example.com/cancel'
        )
        
        assert url == 'https://checkout.stripe.com/session456'
        
        call_args = mock_session_create.call_args[1]
        assert call_args['customer'] == 'cus_existing123'
        assert call_args['line_items'][0]['price'] == 'price_pro'
    
    def test_create_checkout_session_user_not_found(self, client):
        """Test checkout session with non-existent user"""
        client.user_repo.get_user.return_value = None
        
        with pytest.raises(ValueError) as exc_info:
            client.create_checkout_session('user123', 'hobby', 'url1', 'url2')
        
        assert 'User not found' in str(exc_info.value)
    
    def test_create_checkout_session_invalid_plan(self, client):
        """Test checkout session with invalid plan"""
        client.user_repo.get_user.return_value = {
            'user_id': 'user123',
            'email': 'test@example.com'
        }
        
        # Mock create_customer to avoid actual API call
        with patch.object(client, 'create_customer', return_value='cus_123'):
            with pytest.raises(ValueError) as exc_info:
                client.create_checkout_session('user123', 'invalid_plan', 'url1', 'url2')
        
        assert 'Invalid plan' in str(exc_info.value)
    
    @patch('stripe.billing_portal.Session.create')
    def test_create_billing_portal_session_success(self, mock_portal_create, client):
        """Test successful billing portal session creation"""
        client.user_repo.get_user.return_value = {
            'user_id': 'user123',
            'stripe_customer_id': 'cus_123'
        }
        
        mock_portal_create.return_value = Mock(url='https://billing.stripe.com/portal123')
        
        url = client.create_billing_portal_session('user123', 'https://example.com/return')
        
        assert url == 'https://billing.stripe.com/portal123'
        
        mock_portal_create.assert_called_once_with(
            customer='cus_123',
            return_url='https://example.com/return'
        )
    
    def test_create_billing_portal_session_no_customer(self, client):
        """Test billing portal for user without Stripe customer"""
        client.user_repo.get_user.return_value = {'user_id': 'user123'}
        
        with pytest.raises(ValueError) as exc_info:
            client.create_billing_portal_session('user123', 'return_url')
        
        assert 'User has no Stripe customer' in str(exc_info.value)
    
    @patch('stripe.Subscription.modify')
    def test_cancel_subscription_at_period_end(self, mock_modify, client):
        """Test canceling subscription at period end"""
        mock_subscription = Mock(
            status='active',
            cancel_at_period_end=True,
            current_period_end=1234567890
        )
        mock_modify.return_value = mock_subscription
        
        result = client.cancel_subscription('user123', 'sub_123', at_period_end=True)
        
        mock_modify.assert_called_once_with('sub_123', cancel_at_period_end=True)
        
        client.subscription_repo.update_subscription.assert_called_once_with(
            'user123',
            'sub_123',
            {
                'status': 'active',
                'cancel_at_period_end': True
            }
        )
        
        assert result['subscription_id'] == 'sub_123'
        assert result['status'] == 'active'
        assert result['cancel_at_period_end'] is True
    
    @patch('stripe.Subscription.delete')
    def test_cancel_subscription_immediately(self, mock_delete, client):
        """Test immediate subscription cancellation"""
        mock_subscription = Mock(
            status='canceled',
            cancel_at_period_end=False,
            current_period_end=1234567890
        )
        mock_delete.return_value = mock_subscription
        
        result = client.cancel_subscription('user123', 'sub_123', at_period_end=False)
        
        mock_delete.assert_called_once_with('sub_123')
        
        client.subscription_repo.update_subscription.assert_called_once_with(
            'user123',
            'sub_123',
            {
                'status': 'canceled',
                'cancel_at_period_end': False
            }
        )
        
        assert result['status'] == 'canceled'
    
    @patch('stripe.Subscription.retrieve')
    def test_get_subscription_details_success(self, mock_retrieve, client):
        """Test retrieving subscription details"""
        mock_item = Mock(price=Mock(id='price_123'), quantity=1)
        mock_subscription = Mock(
            id='sub_123',
            status='active',
            current_period_start=1234567800,
            current_period_end=1234567890,
            cancel_at_period_end=False,
            items=Mock(data=[mock_item])
        )
        mock_retrieve.return_value = mock_subscription
        
        result = client.get_subscription_details('sub_123')
        
        assert result['id'] == 'sub_123'
        assert result['status'] == 'active'
        assert result['current_period_start'] == 1234567800
        assert result['current_period_end'] == 1234567890
        assert result['cancel_at_period_end'] is False
        assert len(result['items']) == 1
        assert result['items'][0]['price_id'] == 'price_123'


class TestStripeWebhookHandler:
    """Test cases for StripeWebhookHandler class"""
    
    @pytest.fixture
    def handler(self):
        """Create webhook handler instance"""
        with patch('api.core.stripe_client.StripeClient'), \
             patch('api.core.stripe_client.SubscriptionRepository'), \
             patch('api.core.stripe_client.UserRepository'), \
             patch('api.core.stripe_client.settings') as mock_settings:
            mock_settings.STRIPE_WEBHOOK_SECRET = 'whsec_test123'
            handler = StripeWebhookHandler()
            handler.client = Mock()
            handler.subscription_repo = Mock()
            handler.user_repo = Mock()
            return handler
    
    @patch('stripe.Webhook.construct_event')
    def test_handle_webhook_valid_signature(self, mock_construct, handler):
        """Test webhook with valid signature"""
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {'object': {'metadata': {'user_id': 'user123', 'plan_key': 'hobby'}}}
        }
        mock_construct.return_value = mock_event
        
        with patch.object(handler, '_handle_checkout_completed', return_value={'status': 'success'}):
            result = handler.handle_webhook('payload', 'signature')
        
        assert result['status'] == 'success'
        mock_construct.assert_called_once()
    
    @patch('stripe.Webhook.construct_event')
    def test_handle_webhook_invalid_payload(self, mock_construct, handler):
        """Test webhook with invalid payload"""
        mock_construct.side_effect = ValueError('Invalid payload')
        
        with pytest.raises(Exception) as exc_info:
            handler.handle_webhook('invalid', 'signature')
        
        assert 'Invalid payload' in str(exc_info.value)
    
    @patch('stripe.Webhook.construct_event')
    def test_handle_webhook_invalid_signature(self, mock_construct, handler):
        """Test webhook with invalid signature"""
        mock_construct.side_effect = stripe.error.SignatureVerificationError(
            'Invalid sig', 
            sig_header='bad_signature'
        )
        
        with pytest.raises(Exception) as exc_info:
            handler.handle_webhook('payload', 'bad_signature')
        
        assert 'Invalid signature' in str(exc_info.value)
    
    @patch('stripe.Webhook.construct_event')
    def test_handle_webhook_unhandled_event(self, mock_construct, handler):
        """Test webhook with unhandled event type"""
        mock_event = {'type': 'unhandled.event.type', 'data': {}}
        mock_construct.return_value = mock_event
        
        result = handler.handle_webhook('payload', 'signature')
        
        assert result['status'] == 'ignored'
        assert result['event_type'] == 'unhandled.event.type'
    
    def test_handle_checkout_completed(self, handler):
        """Test handling checkout completion"""
        event = {
            'data': {
                'object': {
                    'metadata': {
                        'user_id': 'user123',
                        'plan_key': 'pro'
                    }
                }
            }
        }
        
        result = handler._handle_checkout_completed(event)
        
        assert result['status'] == 'success'
        assert result['action'] == 'checkout_completed'
    
    def test_handle_checkout_completed_missing_metadata(self, handler):
        """Test checkout completion with missing metadata"""
        event = {'data': {'object': {'metadata': {}}}}
        
        result = handler._handle_checkout_completed(event)
        
        assert result['status'] == 'error'
        assert 'Missing metadata' in result['message']
    
    @patch('stripe.Customer.retrieve')
    def test_handle_subscription_created(self, mock_customer_retrieve, handler):
        """Test handling new subscription creation"""
        mock_customer_retrieve.return_value = Mock(metadata={'user_id': 'user123'})
        
        handler.client.plans = {
            'hobby': {'price_id': 'price_hobby_123', 'quota': 100}
        }
        
        event = {
            'data': {
                'object': {
                    'id': 'sub_123',
                    'customer': 'cus_123',
                    'status': 'active',
                    'current_period_end': 1234567890,
                    'items': {
                        'data': [{
                            'price': {'id': 'price_hobby_123'}
                        }]
                    }
                }
            }
        }
        
        result = handler._handle_subscription_created(event)
        
        assert result['status'] == 'success'
        assert result['action'] == 'subscription_created'
        
        handler.subscription_repo.create_subscription.assert_called_once_with(
            user_id='user123',
            stripe_sub_id='sub_123',
            plan_id='hobby',
            status='active',
            current_period_end=1234567890
        )
        
        handler.user_repo.update_user.assert_called_once_with(
            'user123',
            {
                'quota_limit': 100,
                'subscription_plan': 'hobby'
            }
        )
    
    @patch('stripe.Customer.retrieve')
    def test_handle_subscription_updated(self, mock_customer_retrieve, handler):
        """Test handling subscription updates"""
        mock_customer_retrieve.return_value = Mock(metadata={'user_id': 'user123'})
        
        handler.client.plans = {
            'pro': {'price_id': 'price_pro_123', 'quota': 500}
        }
        
        event = {
            'data': {
                'object': {
                    'id': 'sub_123',
                    'customer': 'cus_123',
                    'status': 'active',
                    'current_period_end': 1234567890,
                    'cancel_at_period_end': True,
                    'items': {
                        'data': [{
                            'price': {'id': 'price_pro_123'}
                        }]
                    }
                }
            }
        }
        
        result = handler._handle_subscription_updated(event)
        
        assert result['status'] == 'success'
        assert result['action'] == 'subscription_updated'
        
        handler.subscription_repo.update_subscription.assert_called_once()
        handler.user_repo.update_user.assert_called_once()
    
    @patch('stripe.Customer.retrieve')
    def test_handle_subscription_deleted(self, mock_customer_retrieve, handler):
        """Test handling subscription deletion"""
        mock_customer_retrieve.return_value = Mock(metadata={'user_id': 'user123'})
        
        with patch('time.time', return_value=1234567890):
            event = {
                'data': {
                    'object': {
                        'id': 'sub_123',
                        'customer': 'cus_123'
                    }
                }
            }
            
            result = handler._handle_subscription_deleted(event)
        
        assert result['status'] == 'success'
        assert result['action'] == 'subscription_deleted'
        
        handler.subscription_repo.update_subscription.assert_called_once_with(
            user_id='user123',
            stripe_sub_id='sub_123',
            updates={
                'status': 'canceled',
                'canceled_at': 1234567890
            }
        )
        
        handler.user_repo.update_user.assert_called_once_with(
            'user123',
            {
                'quota_limit': 0,
                'subscription_plan': None
            }
        )
    
    @patch('stripe.Customer.retrieve')
    def test_handle_payment_succeeded_subscription_cycle(self, mock_customer_retrieve, handler):
        """Test handling successful payment for subscription cycle"""
        mock_customer_retrieve.return_value = Mock(metadata={'user_id': 'user123'})
        
        with patch('time.time', return_value=1234567890):
            event = {
                'data': {
                    'object': {
                        'customer': 'cus_123',
                        'billing_reason': 'subscription_cycle'
                    }
                }
            }
            
            result = handler._handle_payment_succeeded(event)
        
        assert result['status'] == 'success'
        assert result['action'] == 'payment_succeeded'
        
        handler.user_repo.update_user.assert_called_once_with(
            'user123',
            {
                'quota_used': 0,
                'quota_reset_at': 1234567890
            }
        )
    
    def test_handle_payment_failed(self, handler):
        """Test handling failed payment"""
        event = {'data': {'object': {}}}
        
        result = handler._handle_payment_failed(event)
        
        assert result['status'] == 'success'
        assert result['action'] == 'payment_failed'