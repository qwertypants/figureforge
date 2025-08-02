from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.core.cache import cache
import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([AllowAny])  # Public endpoint for pricing
def get_pricing(request):
    """
    Get available pricing plans.
    Returns public plan information excluding sensitive Stripe IDs.
    """
    # Try to get from cache first
    cache_key = 'pricing_plans'
    cached_plans = cache.get(cache_key)
    if cached_plans:
        return Response(cached_plans)
    
    try:
        # Determine pricing.json path relative to Django project
        pricing_file = Path(settings.BASE_DIR) / "pricing.json"
        
        if not pricing_file.exists():
            logger.error(f"Pricing file not found at {pricing_file}")
            return Response(
                {"error": "Pricing information temporarily unavailable"},
                status=500
            )
        
        with open(pricing_file) as f:
            plans = json.load(f)
        
        # Filter out sensitive information and inactive plans
        public_plans = [
            {
                "plan_id": plan["plan_id"],
                "name": plan["name"],
                "price_usd_month": plan["price_usd_month"],
                "images_per_month": plan["images_per_month"],
                "batch_cap": plan["batch_cap"],
                "features": plan.get("features", []),  # Optional features list
                "popular": plan.get("popular", False),  # Optional popular flag
            }
            for plan in plans if plan.get("active", True)
        ]
        
        # Cache for 1 hour
        cache.set(cache_key, public_plans, 3600)
        
        return Response(public_plans)
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in pricing file: {e}")
        return Response(
            {"error": "Invalid pricing configuration"},
            status=500
        )
    except Exception as e:
        logger.error(f"Error loading pricing: {e}")
        return Response(
            {"error": "Unable to load pricing information"},
            status=500
        )
