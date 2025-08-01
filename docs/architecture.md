# Architecture

## Stack
- **Frontend**: React SPA (S3 + CloudFront)
- **Backend**: Django REST Framework on AWS Lambda (Zappa/Serverless) behind API Gateway
- **Auth**: Amazon Cognito (email/password + Google/Apple)
- **Database**: DynamoDB (single-table)
- **Storage**: S3
- **CDN**: CloudFront
- **Queue/Async**: SQS + Worker Lambda
- **Image Provider**: fal.ai (switchable to Bedrock/others)
- **Billing**: Stripe (Checkout + Billing Portal + Webhooks)
- **Observability**: CloudWatch (logs + custom metrics)

## Text Diagram
```
React SPA (S3+CloudFront)
        |
    API Gateway
        |
  Lambda (Django REST)
        |         \-- Stripe Webhooks
     DynamoDB     Stripe
        |
       SQS  <---- Lambda (enqueue jobs)
        |
 Worker Lambda (LLM prompt → fal.ai)
        |
   S3 (images) ---- CloudFront (signed/token-gated)
```
