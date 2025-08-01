# API Spec (v1)

Base: `/api/v1`

## Auth / User
### `GET /me`
- Returns profile, quota, plan, role.

### `POST /me/username`
- Body: `{ "username": "anon" }`

## Pricing / Billing
### `GET /pricing`
- Returns all active plans.

### `POST /billing/checkout-session`
- Body: `{ "plan_id": "pro_1000" }`
- Returns: `{ "url": "<stripe_checkout_url>" }`

### `GET /billing/portal`
- Returns: `{ "url": "<stripe_portal_url>" }`

### `POST /webhooks/stripe`
- Unauthenticated. Validates signature.

## Generation
### `POST /generate`
- Body: `{ "filters": {...}, "batch_size": 1-4 }`
- Returns: `{ "job_id": "<uuid>" }`

### `GET /jobs/:job_id`
- Returns `{ "status": "queued|running|succeeded|failed", "image_ids": [...] }`

## Images
### `GET /images/public?tags=pose:standing&cursor=...`
- Paid users: full public gallery.
- Non-paid: limited teaser.

### `GET /images/:id`
- Returns image metadata.

### `POST /images/:id/favorite`
### `DELETE /images/:id/favorite`

### `POST /images/:id/report`
- Body: `{ "reasons": ["nsfw", ...], "details": "optional" }`

## Galleries
### `POST /galleries`
### `GET /galleries/:id`
### `POST /galleries/:id/images`

## Admin
### `GET /admin/reports?status=human_pending`
### `POST /admin/reports/:id/resolve`
- Body: `{ "action": "unflag" | "remove" }`

### `GET /admin/feature-flags`
### `POST /admin/feature-flags/:name`
- Body: `{ "enabled": true|false, "value": any }`
