# Tasks

## Backend (✅ COMPLETED)
- [x] Scaffold Django REST API for Lambda (Zappa/Serverless).
- [x] Integrate Cognito JWT validation middleware.
- [x] Implement DynamoDB single-table CRUD helpers.
- [x] Implement `/generate` (enqueue SQS job).
- [x] Implement Job Worker Lambda (LLM prompt + fal.ai → S3/DynamoDB).
- [x] Implement `/jobs/:id` polling endpoint.
- [x] Stripe webhook handler (subscription lifecycle, quota sync).
- [x] Feature flags endpoint.
- [x] Admin moderation endpoints.
- [x] Magic link authentication flow.
- [x] Pricing endpoint for public access.
- [x] User stats and profile management.
- [x] Image metadata updates and favorites.

## Frontend
- [ ] React SPA bootstrap (Vite).
- [ ] Auth flow with Cognito (email/password + social).
- [ ] Filter panel with enums (mobile-first).
- [ ] Generate screen: batch size selector (1–4).
- [ ] Job status toast + skeleton grid.
- [ ] Infinite-scroll galleries (public, my library, favorites).
- [ ] Image flag dialog + reason enum.
- [ ] Stripe checkout + billing portal routing.
- [ ] Admin moderation UI (list + resolve).

## Infra
- [ ] S3 buckets: SPA hosting + images.
- [ ] CloudFront distributions (SPA + images).
- [ ] DynamoDB: on-demand + PITR.
- [ ] SQS + DLQ (with redrive).
- [ ] IAM roles/policies (least privilege).
- [ ] CloudWatch dashboards/alarms.
