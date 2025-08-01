# FigureForge Deployment Checklist

## Pre-Deployment Setup

### AWS Account Setup
- [ ] Create AWS account
- [ ] Configure AWS CLI with credentials
- [ ] Set up appropriate IAM roles and policies

### AWS Resources
- [ ] Create DynamoDB table (`figureforge-main`)
  - [ ] Configure single-table design
  - [ ] Set up GSI for queries
- [ ] Create S3 bucket for images (`figureforge-images`)
  - [ ] Configure CORS policy
  - [ ] Set up lifecycle rules for cost optimization
- [ ] Create SQS queue (`figureforge-jobs`)
  - [ ] Configure dead letter queue
  - [ ] Set visibility timeout appropriately
- [ ] Set up Cognito User Pool
  - [ ] Configure app client
  - [ ] Set up user attributes
  - [ ] Configure password policies
- [ ] Create CloudFront distribution
  - [ ] Configure origins for S3 and API
  - [ ] Set up custom domain (optional)

### Third-Party Services
- [ ] Create Stripe account
  - [ ] Get API keys
  - [ ] Configure webhook endpoint
  - [ ] Set up products and pricing
- [ ] Create fal.ai account
  - [ ] Get API key
  - [ ] Verify API limits and pricing

## Backend Deployment

### Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Fill in all environment variables:
  - [ ] Django SECRET_KEY
  - [ ] AWS credentials
  - [ ] DynamoDB table name
  - [ ] S3 bucket name
  - [ ] SQS queue URL
  - [ ] Cognito configuration
  - [ ] Stripe keys
  - [ ] fal.ai API key

### Django Setup
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Test setup: `python test_setup.py`
- [ ] Create superuser (optional): `python manage.py createsuperuser`

### Zappa Deployment
- [ ] Configure `zappa_settings.json`
  - [ ] Update S3 bucket for deployments
  - [ ] Set correct AWS region
  - [ ] Configure domain (if using custom domain)
- [ ] Deploy to development: `zappa deploy dev`
- [ ] Test API endpoints
- [ ] Deploy to production: `zappa deploy production`
- [ ] Update API Gateway settings if needed

### Worker Lambda
- [ ] Package worker function:
  ```bash
  cd backend/worker
  pip install -r requirements.txt -t .
  zip -r worker.zip .
  ```
- [ ] Create Lambda function in AWS Console
- [ ] Upload worker.zip
- [ ] Configure environment variables
- [ ] Set up SQS trigger
- [ ] Configure Lambda timeout and memory
- [ ] Test with sample SQS message

## Frontend Deployment

### Build Configuration
- [ ] Update API endpoint in frontend config
- [ ] Configure Stripe publishable key
- [ ] Set Cognito configuration
- [ ] Update any environment-specific settings

### Build and Deploy
- [ ] Install dependencies: `npm install`
- [ ] Build production bundle: `npm run build`
- [ ] Create S3 bucket for frontend hosting
- [ ] Enable static website hosting
- [ ] Upload build files:
  ```bash
  aws s3 sync dist/ s3://your-frontend-bucket --delete
  ```
- [ ] Configure CloudFront distribution
- [ ] Set up custom domain (optional)
- [ ] Configure SSL certificate

## Post-Deployment

### Testing
- [ ] Test user registration/login flow
- [ ] Test image generation workflow
- [ ] Test subscription checkout
- [ ] Test Stripe webhooks
- [ ] Verify image storage and retrieval
- [ ] Check error handling and logging

### Monitoring Setup
- [ ] Configure CloudWatch alarms
  - [ ] Lambda errors
  - [ ] API Gateway 4xx/5xx errors
  - [ ] DynamoDB throttling
  - [ ] SQS queue depth
- [ ] Set up CloudWatch Logs retention
- [ ] Configure billing alerts

### Security Review
- [ ] Review IAM permissions (principle of least privilege)
- [ ] Ensure all secrets are in environment variables
- [ ] Verify CORS configuration
- [ ] Check API rate limiting
- [ ] Review Cognito security settings
- [ ] Ensure S3 buckets are not publicly accessible

### Documentation
- [ ] Update README with production URLs
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document rollback procedures

## Maintenance

### Regular Tasks
- [ ] Monitor CloudWatch logs
- [ ] Review AWS costs
- [ ] Update dependencies regularly
- [ ] Backup critical data
- [ ] Review and rotate API keys

### Scaling Considerations
- [ ] Monitor Lambda cold starts
- [ ] Review DynamoDB capacity
- [ ] Optimize S3 storage costs
- [ ] Consider Reserved Capacity for predictable workloads

## Rollback Plan

1. **API Rollback**:
   ```bash
   zappa rollback production -n 1
   ```

2. **Frontend Rollback**:
   - Keep previous build artifacts
   - Re-sync previous version to S3
   - Invalidate CloudFront cache

3. **Database Rollback**:
   - DynamoDB point-in-time recovery
   - Restore from backups if available

## Support Contacts

- AWS Support: [Your support plan details]
- Stripe Support: support@stripe.com
- fal.ai Support: [Support contact]
- Domain Registrar: [If using custom domain]

## Notes

- Always test in development environment first
- Keep staging environment as close to production as possible
- Document any deviations from this checklist
- Review and update this checklist regularly
