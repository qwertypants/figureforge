# Analytics & Logging

## Observability
- **CloudWatch** logs & metrics only (MVP).
- Custom metrics:
  - `images_generated_total`
  - `images_generated_cost_total_cents`
  - `images_flagged_total`
  - `jobs_failed_total`
  - `quota_exhausted_total`
  - `active_subscriptions`
  - DAU (hits on /me or /app/*)

## Log Format
- JSON structured logs with: `timestamp, level, request_id, user_id, route, duration_ms, cost_cents`.
