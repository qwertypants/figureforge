# Product Goals

## Purpose
Generate SFW human figure reference images for hobbyist artists. Users pick predefined filters, click **Generate**, and receive unique, auto‑tagged images.

## Primary Goals
- Simple, mobile-first web app for fast figure generation.
- Paid-only generation (Stripe) before any generation occurs.
- Auto-tagged images for easy, *tag-only* search and organization.
- Public gallery (very limited for non‑subscribers) to attract new users.
- Host on AWS: S3, CloudFront, API Gateway, Lambda, DynamoDB, Cognito, SQS.
- Backend: **Django REST Framework** (on Lambda) + tiny **React SPA** frontend.

## Non-Goals (MVP)
- No free trial.
- No full-text search.
- No deterministic regeneration (no seeds).
- No overage billing (only upsell near threshold).
- No keyboard shortcuts/power user flows.
- No strict latency/SLA targets (prototype).

## Success Metrics (initial)
- DAU (paid users).
- Retention.
- Images generated per paying user per month.
- Profit margin per plan (provider cost vs. revenue).
