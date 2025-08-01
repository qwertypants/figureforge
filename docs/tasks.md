# Tasks

## Backend
- [ ] Scaffold Django REST API for Lambda (Zappa/Serverless).
- [ ] Integrate Cognito JWT validation middleware.
- [ ] Implement DynamoDB single-table CRUD helpers.
- [ ] Implement `/generate` (enqueue SQS job).
- [ ] Implement Job Worker Lambda (LLM prompt + fal.ai → S3/DynamoDB).
- [ ] Implement `/jobs/:id` polling endpoint.
- [ ] Stripe webhook handler (subscription lifecycle, quota sync).
- [ ] Feature flags endpoint.
- [ ] Admin moderation endpoints.

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
