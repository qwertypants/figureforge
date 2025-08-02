import stripe
import json
import os
import sys
from pathlib import Path

# Load Stripe API key from environment
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
if not stripe.api_key:
    print("Error: STRIPE_SECRET_KEY environment variable not set")
    sys.exit(1)

# Determine pricing.json path
pricing_file = Path(__file__).parent / "pricing.json"
if not pricing_file.exists():
    print(f"Error: {pricing_file} not found")
    sys.exit(1)

# Create backup before modifying
backup_file = pricing_file.with_suffix('.json.backup')
try:
    with open(pricing_file) as f:
        plans = json.load(f)
    # Save backup
    with open(backup_file, 'w') as f:
        json.dump(plans, f, indent=2)
    print(f"Created backup at {backup_file}")
except Exception as e:
    print(f"Error reading pricing.json: {e}")
    sys.exit(1)

# Check for existing products to avoid duplicates
try:
    existing_products = stripe.Product.list(limit=100)
    product_map = {p.name: p for p in existing_products.data}
except stripe.error.StripeError as e:
    print(f"Error fetching existing products: {e}")
    sys.exit(1)

for plan in plans:
    try:
        print(f"\nSyncing plan: {plan['name']}")
        
        # Check if product already exists
        if plan['name'] in product_map:
            product = product_map[plan['name']]
            print(f"  Using existing product: {product.id}")
        else:
            # Create new product with metadata
            product = stripe.Product.create(
                name=plan["name"],
                metadata={
                    "plan_id": plan["plan_id"],
                    "images_per_month": str(plan["images_per_month"])
                }
            )
            print(f"  Created new product: {product.id}")
        
        # Create price (prices are immutable, so we always create new ones)
        price = stripe.Price.create(
            unit_amount=int(plan["price_usd_month"] * 100),
            currency="usd",
            recurring={"interval": "month"},
            product=product.id,
            metadata={"plan_id": plan["plan_id"]}
        )
        plan["stripe_price_id"] = price.id
        print(f"  Created Stripe price ID: {price.id}")
        
    except stripe.error.StripeError as e:
        print(f"  Error syncing {plan['name']}: {e}")
        print("  Aborting sync to prevent partial updates")
        sys.exit(1)

# Write updated pricing.json
try:
    with open(pricing_file, "w") as f:
        json.dump(plans, f, indent=2)
        f.write('\n')  # Add trailing newline
    print("\n✅ pricing.json updated with Stripe price IDs")
    print(f"Backup saved at: {backup_file}")
except Exception as e:
    print(f"\nError writing pricing.json: {e}")
    print("Attempting to restore from backup...")
    try:
        with open(backup_file) as f:
            backup_data = json.load(f)
        with open(pricing_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        print("Restored from backup")
    except Exception as restore_error:
        print(f"Failed to restore backup: {restore_error}")
    sys.exit(1)
