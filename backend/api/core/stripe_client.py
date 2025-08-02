"""
Stripe client for subscription management
Handles subscription creation, updates, and webhook processing
"""

import stripe
import time
from typing import Dict, List, Optional, Any
from django.conf import settings
from api.core.dynamodb_utils import SubscriptionRepository, UserRepository


class StripeClient:
    """Client for interacting with Stripe API"""
    
    def __init__(self):
        self.subscription_repo = SubscriptionRepository()
        self.user_repo = UserRepository()
        self._stripe_configured = False
        
        # Define subscription plans
        self.plans = {
            "hobby": {
                "price_id": "price_hobby",  # Replace with actual Stripe price ID
                "name": "Hobby",
                "price_cents": 999,  # $9.99
                "quota": 100,  # 100 images per month
                "features": [
                    "100 images per month",
                    "Basic models",
                    "Standard resolution",
                    "Community gallery access"
                ]
            },
            "pro": {
                "price_id": "price_pro",  # Replace with actual Stripe price ID
                "name": "Pro",
                "price_cents": 2499,  # $24.99
                "quota": 500,  # 500 images per month
                "features": [
                    "500 images per month",
                    "All models including premium",
                    "High resolution",
                    "Priority generation",
                    "Private galleries"
                ]
            },
            "studio": {
                "price_id": "price_studio",  # Replace with actual Stripe price ID
                "name": "Studio",
                "price_cents": 9999,  # $99.99
                "quota": 2000,  # 2000 images per month
                "features": [
                    "2000 images per month",
                    "All models with priority access",
                    "Maximum resolution",
                    "Batch processing",
                    "API access",
                    "Custom models (coming soon)"
                ]
            }
        }
    
    def _ensure_stripe_configured(self):
        """Configure Stripe API key if not already done"""
        if not self._stripe_configured:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            self._stripe_configured = True
    
    def create_customer(self, user_id: str, email: str) -> str:
        """Create a Stripe customer for a user"""
        self._ensure_stripe_configured()
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={
                    "user_id": user_id
                }
            )
            
            # Update user with Stripe customer ID
            self.user_repo.update_user(user_id, {
                "stripe_customer_id": customer.id
            })
            
            return customer.id
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe customer: {str(e)}")
    
    def create_checkout_session(self, user_id: str, plan_key: str, 
                              success_url: str, cancel_url: str) -> str:
        """Create a Stripe checkout session for subscription"""
        self._ensure_stripe_configured()
        user = self.user_repo.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Get or create Stripe customer
        customer_id = user.get("stripe_customer_id")
        if not customer_id:
            customer_id = self.create_customer(user_id, user["email"])
        
        plan = self.plans.get(plan_key)
        if not plan:
            raise ValueError("Invalid plan")
        
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": plan["price_id"],
                    "quantity": 1
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": user_id,
                    "plan_key": plan_key
                }
            )
            
            return session.url
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create checkout session: {str(e)}")
    
    def create_billing_portal_session(self, user_id: str, return_url: str) -> str:
        """Create a Stripe billing portal session"""
        self._ensure_stripe_configured()
        user = self.user_repo.get_user(user_id)
        if not user or not user.get("stripe_customer_id"):
            raise ValueError("User has no Stripe customer")
        
        try:
            session = stripe.billing_portal.Session.create(
                customer=user["stripe_customer_id"],
                return_url=return_url
            )
            
            return session.url
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create billing portal session: {str(e)}")
    
    def cancel_subscription(self, user_id: str, subscription_id: str, 
                          at_period_end: bool = True) -> Dict:
        """Cancel a subscription"""
        self._ensure_stripe_configured()
        try:
            if at_period_end:
                # Cancel at end of billing period
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                # Cancel immediately
                subscription = stripe.Subscription.delete(subscription_id)
            
            # Update in database
            self.subscription_repo.update_subscription(
                user_id, 
                subscription_id,
                {
                    "status": "canceled" if not at_period_end else "active",
                    "cancel_at_period_end": at_period_end
                }
            )
            
            return {
                "subscription_id": subscription_id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "current_period_end": subscription.current_period_end
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    def get_subscription_details(self, subscription_id: str) -> Dict:
        """Get subscription details from Stripe"""
        self._ensure_stripe_configured()
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "items": [{
                    "price_id": item.price.id,
                    "quantity": item.quantity
                } for item in subscription.items.data]
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to retrieve subscription: {str(e)}")


class StripeWebhookHandler:
    """Handle Stripe webhook events"""
    
    def __init__(self):
        self.client = StripeClient()
        self.subscription_repo = SubscriptionRepository()
        self.user_repo = UserRepository()
        self._stripe_configured = False
    
    def _ensure_stripe_configured(self):
        """Configure Stripe API key if not already done"""
        if not self._stripe_configured:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            self._stripe_configured = True
    
    def handle_webhook(self, payload: str, signature: str) -> Dict:
        """Process a Stripe webhook"""
        self._ensure_stripe_configured()
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise Exception("Invalid signature")
        
        # Handle different event types
        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed
        }
        
        handler = handlers.get(event["type"])
        if handler:
            return handler(event)
        
        return {"status": "ignored", "event_type": event["type"]}
    
    def _handle_checkout_completed(self, event: Dict) -> Dict:
        """Handle successful checkout"""
        session = event["data"]["object"]
        
        # Get metadata
        user_id = session["metadata"].get("user_id")
        plan_key = session["metadata"].get("plan_key")
        
        if not user_id or not plan_key:
            return {"status": "error", "message": "Missing metadata"}
        
        # Subscription will be created via subscription.created event
        return {"status": "success", "action": "checkout_completed"}
    
    def _handle_subscription_created(self, event: Dict) -> Dict:
        """Handle new subscription creation"""
        self._ensure_stripe_configured()
        subscription = event["data"]["object"]
        
        # Get user from customer
        customer_id = subscription["customer"]
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get("user_id")
        
        if not user_id:
            return {"status": "error", "message": "No user_id in customer metadata"}
        
        # Determine plan from price ID
        price_id = subscription["items"]["data"][0]["price"]["id"]
        plan_key = None
        for key, plan in self.client.plans.items():
            if plan["price_id"] == price_id:
                plan_key = key
                break
        
        if not plan_key:
            return {"status": "error", "message": "Unknown price ID"}
        
        # Create subscription record
        self.subscription_repo.create_subscription(
            user_id=user_id,
            stripe_sub_id=subscription["id"],
            plan_id=plan_key,
            status=subscription["status"],
            current_period_end=subscription["current_period_end"]
        )
        
        # Update user quota
        plan = self.client.plans[plan_key]
        self.user_repo.update_user(user_id, {
            "quota_limit": plan["quota"],
            "subscription_plan": plan_key
        })
        
        return {"status": "success", "action": "subscription_created"}
    
    def _handle_subscription_updated(self, event: Dict) -> Dict:
        """Handle subscription updates"""
        self._ensure_stripe_configured()
        subscription = event["data"]["object"]
        
        # Get user from customer
        customer_id = subscription["customer"]
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get("user_id")
        
        if not user_id:
            return {"status": "error", "message": "No user_id in customer metadata"}
        
        # Update subscription record
        self.subscription_repo.update_subscription(
            user_id=user_id,
            stripe_sub_id=subscription["id"],
            updates={
                "status": subscription["status"],
                "current_period_end": subscription["current_period_end"],
                "cancel_at_period_end": subscription.get("cancel_at_period_end", False)
            }
        )
        
        # Update user quota if plan changed
        price_id = subscription["items"]["data"][0]["price"]["id"]
        for key, plan in self.client.plans.items():
            if plan["price_id"] == price_id:
                self.user_repo.update_user(user_id, {
                    "quota_limit": plan["quota"],
                    "subscription_plan": key
                })
                break
        
        return {"status": "success", "action": "subscription_updated"}
    
    def _handle_subscription_deleted(self, event: Dict) -> Dict:
        """Handle subscription cancellation"""
        self._ensure_stripe_configured()
        subscription = event["data"]["object"]
        
        # Get user from customer
        customer_id = subscription["customer"]
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata.get("user_id")
        
        if not user_id:
            return {"status": "error", "message": "No user_id in customer metadata"}
        
        # Update subscription status
        self.subscription_repo.update_subscription(
            user_id=user_id,
            stripe_sub_id=subscription["id"],
            updates={
                "status": "canceled",
                "canceled_at": int(time.time())
            }
        )
        
        # Reset user quota
        self.user_repo.update_user(user_id, {
            "quota_limit": 0,
            "subscription_plan": None
        })
        
        return {"status": "success", "action": "subscription_deleted"}
    
    def _handle_payment_succeeded(self, event: Dict) -> Dict:
        """Handle successful payment"""
        self._ensure_stripe_configured()
        invoice = event["data"]["object"]
        
        # Reset monthly quota on successful payment
        if invoice.get("billing_reason") == "subscription_cycle":
            customer_id = invoice["customer"]
            customer = stripe.Customer.retrieve(customer_id)
            user_id = customer.metadata.get("user_id")
            
            if user_id:
                self.user_repo.update_user(user_id, {
                    "quota_used": 0,
                    "quota_reset_at": int(time.time())
                })
        
        return {"status": "success", "action": "payment_succeeded"}
    
    def _handle_payment_failed(self, event: Dict) -> Dict:
        """Handle failed payment"""
        # Could send notification email, update user status, etc.
        return {"status": "success", "action": "payment_failed"}
