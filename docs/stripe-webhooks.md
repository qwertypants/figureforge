# Stripe Webhooks

## Required Events
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

## Handler Responsibilities
- Map Stripe customer → Cognito user.
- Update `plan_id`, `quota_remaining`, `quota_reset_at`.
- Handle failed payments: mark `past_due` (cut access based on policy).
- Log all events for audit.

## Pseudocode
```python
def stripe_webhook(event):
    t = event['type']
    obj = event['data']['object']

    if t.startswith("customer.subscription."):
        upsert_subscription(obj)
        sync_quota(obj)

    elif t == "invoice.payment_failed":
        mark_past_due(obj['customer'])

    return {"status": "ok"}
```
