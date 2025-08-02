import stripe
import json

stripe.api_key = "sk_test_..."  # Replace with your real key or load from env

with open("pricing.json") as f:
    plans = json.load(f)

for plan in plans:
    print(f"Syncing plan: {plan['name']}")
    product = stripe.Product.create(name=plan["name"])
    price = stripe.Price.create(
        unit_amount=int(plan["price_usd_month"] * 100),
        currency="usd",
        recurring={"interval": "month"},
        product=product.id,
    )
    plan["stripe_price_id"] = price.id
    print(f" → Created Stripe price ID: {price.id}")

with open("pricing.json", "w") as f:
    json.dump(plans, f, indent=2)

print("✅ pricing.json updated with Stripe price IDs")
