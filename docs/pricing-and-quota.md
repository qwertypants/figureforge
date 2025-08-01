# Pricing & Quotas

## Strategy
- Tiered (Starter, Pro, Studio, etc.).
- Monthly quotas (no daily caps).
- Upsell at ~90% of monthly quota.
- No free trial; limited free gallery for non-subscribers.
- Margin rule: price >= (provider_cost * margin).

## Quota Enforcement
- On `/generate`, check `quota_remaining >= batch_size`.
- On success → decrement by `batch_size`.
- Stripe webhooks reset `quota_remaining` each billing cycle.

## Stripe
- Checkout sessions for subscription purchase.
- Billing Portal for self-service.
- Webhooks handled:
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_succeeded`
  - `invoice.payment_failed`

## Plan Item (example)
```json
{
  "pk": "PLAN#pro_1000",
  "sk": "META",
  "price_usd_month": 14.00,
  "images_per_month": 1000,
  "batch_cap": 4,
  "oversell_upsell_threshold_pct": 0.9,
  "active": true
}
```
