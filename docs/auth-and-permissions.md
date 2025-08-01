# Auth & Permissions

## Auth
- **Amazon Cognito** (User Pool)
  - Email/password
  - Social: Google, Apple (optional)
- JWT validated by API Gateway / backend.

## Roles
- `user` (default)
- `admin` (you)

## Access Rules
- **Generation**: paid users only (must have active Stripe sub).
- **Public gallery**: everyone sees a limited subset (config).
- **Private galleries**: only owner can see.
- **Direct links**: only paid users (token-gated/signed URLs).
- **Admin**: moderation dashboard.

## User Profile
- Username (can be "anon").
- Users can choose whether their generations are publicly attributed or anonymous.
