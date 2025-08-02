# FigureForge API Specification

Base URL: `/api`

## Authentication

All authenticated endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication & User Management

#### Get Current User
`GET /api/auth/user/`
- Returns current user profile with subscription info
- Response: `{ "id": "user_123", "email": "user@example.com", "username": "artist", "subscription": {...}, "quota": {...} }`

#### Update User Profile
`POST /api/auth/user/update/`
- Body: `{ "username": "new_username", "display_name": "Display Name" }`
- Updates user profile information

#### Get User Stats
`GET /api/auth/user/stats/`
- Returns usage statistics for the current user
- Response: `{ "images_generated": 150, "images_remaining": 50, "subscription_tier": "pro" }`

#### Verify Token
`POST /api/auth/verify/`
- Verifies if the current JWT token is valid
- Response: `{ "valid": true, "user_id": "user_123" }`

#### Delete Account
`DELETE /api/auth/delete/`
- Permanently deletes the user account
- Requires confirmation

### Magic Link Authentication

#### Request Magic Link
`POST /api/auth/magic-link/request/`
- Body: `{ "email": "user@example.com" }`
- Sends a magic link to the email address

#### Verify Magic Link
`POST /api/auth/magic-link/verify/`
- Body: `{ "email": "user@example.com", "code": "123456" }`
- Verifies the magic link code and returns JWT tokens

#### Check Magic Link User
`POST /api/auth/magic-link/check-user/`
- Body: `{ "email": "user@example.com" }`
- Checks if a user exists with the given email

### Image Generation

#### Generate Images
`POST /api/images/generate/`
- Body: 
  ```json
  {
    "prompt": "figure drawing prompt",
    "filters": {
      "body_type": "athletic",
      "pose": "standing",
      "lighting": "dramatic",
      "clothing": "casual",
      "background": "simple"
    },
    "batch_size": 1,
    "model": "flux-pro"
  }
  ```
- Returns: `{ "job_id": "job_uuid", "status": "queued" }`

#### Get Job Status
`GET /api/images/job/<job_id>/`
- Returns job status and generated images
- Response: 
  ```json
  {
    "job_id": "job_uuid",
    "status": "completed",
    "images": [
      {
        "id": "img_123",
        "url": "https://cdn.example.com/image.jpg",
        "thumbnail_url": "https://cdn.example.com/thumb.jpg"
      }
    ]
  }
  ```

#### Get User Images
`GET /api/images/user/`
- Query params: `?limit=20&offset=0&tag=pose:standing`
- Returns paginated list of user's generated images

#### Get Public Gallery
`GET /api/images/gallery/`
- Query params: `?limit=20&offset=0&tags=lighting:dramatic,pose:action`
- Returns public gallery images (filtered based on user subscription)

#### Get Image Details
`GET /api/images/<image_id>/`
- Returns detailed metadata for a specific image

#### Delete Image
`DELETE /api/images/<image_id>/delete/`
- Deletes an image (owner only)

#### Update Image Metadata
`PATCH /api/images/<image_id>/update/`
- Body: `{ "tags": ["tag1", "tag2"], "is_public": true }`
- Updates image metadata

#### Favorite/Unfavorite Image
`POST /api/images/<image_id>/favorite/`
- Toggles favorite status for an image

#### Get Generation Models
`GET /api/images/models/`
- Returns available AI models for image generation
- Response: `{ "models": [{"id": "flux-pro", "name": "FLUX Pro", "credits": 2}] }`

### Pricing

#### Get Pricing
`GET /api/pricing/`
- Returns current pricing information for all plans
- Public endpoint (no authentication required)

### Subscription Management

#### Get Subscription Plans
`GET /api/subscriptions/plans/`
- Returns all available subscription plans
- Response includes plan features and pricing

#### Get Current Subscription
`GET /api/subscriptions/current/`
- Returns current user's subscription details

#### Create Checkout Session
`POST /api/subscriptions/checkout/`
- Body: `{ "plan_id": "pro_monthly", "success_url": "...", "cancel_url": "..." }`
- Returns: `{ "checkout_url": "https://checkout.stripe.com/..." }`

#### Create Billing Portal Session
`POST /api/subscriptions/portal/`
- Returns: `{ "portal_url": "https://billing.stripe.com/..." }`

#### Cancel Subscription
`POST /api/subscriptions/cancel/`
- Cancels subscription at period end

#### Reactivate Subscription
`POST /api/subscriptions/reactivate/`
- Reactivates a cancelled subscription

#### Get Billing History
`GET /api/subscriptions/history/`
- Returns user's billing history

#### Update Payment Method
`POST /api/subscriptions/payment-method/`
- Body: `{ "payment_method_id": "pm_xxx" }`
- Updates default payment method

### Webhooks

#### Stripe Webhook
`POST /api/webhooks/stripe/`
- Handles Stripe webhook events
- Requires valid Stripe signature header

#### Webhook Health Check
`GET /api/webhooks/health/`
- Returns webhook system health status

## Error Responses

All endpoints may return error responses in the following format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  }
}
```

Common error codes:
- `AUTHENTICATION_REQUIRED`: Missing or invalid authentication
- `INSUFFICIENT_QUOTA`: User has exceeded their generation quota
- `INVALID_REQUEST`: Request validation failed
- `NOT_FOUND`: Resource not found
- `PERMISSION_DENIED`: User lacks permission for this action

## Rate Limiting

- Authenticated requests: 1000/hour per user
- Image generation: Based on subscription tier
- Public gallery: 100 requests/minute for unauthenticated users

## Pagination

List endpoints support pagination via query parameters:
- `limit`: Number of items per page (default: 20, max: 100)
- `offset`: Number of items to skip

Response includes:
```json
{
  "results": [...],
  "count": 150,
  "next": "/api/images/user/?limit=20&offset=20",
  "previous": null
}
```