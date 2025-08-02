# Auth & Permissions

## Auth
- **Amazon Cognito** (User Pool)
  - Email/password
  - Magic Link authentication (passwordless)
  - Social: Google, Apple (optional)
- JWT validated by API Gateway / backend.
- **Magic Link Flow**:
  1. User requests magic link with email
  2. Cognito Lambda generates 6-digit code
  3. Email sent with verification code
  4. User enters code to receive JWT tokens
  5. No password required for sign-in

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
