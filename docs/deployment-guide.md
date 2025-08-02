# FigureForge Deployment Guide

This guide covers deploying FigureForge to AWS using Lambda, S3, CloudFront, and other AWS services.

## Prerequisites

1. **AWS CLI configured**: Run `aws configure` with your credentials
2. **Python environment**: Python 3.10+ with virtualenv
3. **Node.js**: Version 20+ for frontend build
4. **Domain name** (optional): For custom domains

## Step 1: Deploy Backend with Zappa

### 1.1 Prepare Environment

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1.2 Create S3 Bucket for Deployments

```bash
aws s3 mb s3://figureforge-zappa-deployments --region us-east-1
```

### 1.3 Deploy to Development

```bash
zappa deploy dev
```

Note the API Gateway URL provided after deployment (e.g., `https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev`)

### 1.4 Deploy to Production

```bash
zappa deploy production
```

### 1.5 Update Deployed Function

```bash
zappa update dev  # or production
```

## Step 2: Set Up AWS Services

### 2.1 Create DynamoDB Table

```bash
aws dynamodb create-table \
  --table-name figureforge-table \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 2.2 Create S3 Bucket for Images

```bash
aws s3 mb s3://figureforge-images --region us-east-1

# Create bucket policy file
cat > s3-bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::figureforge-images/*"
  }]
}
EOF

# Apply policy
aws s3api put-bucket-policy --bucket figureforge-images \
  --policy file://s3-bucket-policy.json
```

### 2.3 Create SQS Queue

```bash
aws sqs create-queue \
  --queue-name figureforge-image-generation \
  --region us-east-1
```

### 2.4 Set Up Cognito User Pool

```bash
aws cognito-idp create-user-pool \
  --pool-name figureforge-users \
  --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true}" \
  --auto-verified-attributes email \
  --region us-east-1
```

## Step 3: Configure Magic Link Authentication

### 3.1 Deploy Cognito Lambda Triggers

```bash
cd backend

# Install Serverless Framework if not already installed
npm install -g serverless

# Deploy the Cognito triggers
serverless deploy --config serverless-cognito.yml \
  --param="user-pool-name=figureforge-users" \
  --param="dynamodb-table=figureforge-table" \
  --param="frontend-url=https://your-frontend-url.com" \
  --param="from-email=noreply@yourdomain.com"
```

### 3.2 Configure SES for Email

```bash
# Verify sender email
aws ses verify-email-identity --email-address noreply@yourdomain.com

# For production, request SES production access
```

### 3.3 Update Cognito App Client

```bash
# Get User Pool ID and App Client ID
USER_POOL_ID=$(aws cognito-idp list-user-pools --max-results 10 \
  --query "UserPools[?Name=='figureforge-users'].Id" --output text)

APP_CLIENT_ID=$(aws cognito-idp list-user-pool-clients \
  --user-pool-id $USER_POOL_ID \
  --query "UserPoolClients[0].ClientId" --output text)

# Enable CUSTOM_AUTH flow
aws cognito-idp update-user-pool-client \
  --user-pool-id $USER_POOL_ID \
  --client-id $APP_CLIENT_ID \
  --explicit-auth-flows ALLOW_CUSTOM_AUTH ALLOW_USER_SRP_AUTH ALLOW_REFRESH_TOKEN_AUTH
```

## Step 4: Deploy Worker Lambda

### 4.1 Create IAM Role

```bash
# Create trust policy
cat > lambda-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": "lambda.amazonaws.com"
    },
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name figureforge-lambda-role \
  --assume-role-policy-document file://lambda-trust-policy.json

# Attach basic execution policy
aws iam attach-role-policy \
  --role-name figureforge-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create custom policy
cat > lambda-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::figureforge-images/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:*:table/figureforge-table"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:us-east-1:*:figureforge-image-generation"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name figureforge-lambda-role \
  --policy-name figureforge-lambda-policy \
  --policy-document file://lambda-policy.json
```

### 4.2 Package and Deploy Worker

```bash
cd backend/worker

# Create deployment package
mkdir package
pip install -r requirements.txt -t package/
cp handler.py package/
cd package
zip -r ../worker.zip .
cd ..

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create Lambda function
aws lambda create-function \
  --function-name figureforge-worker \
  --runtime python3.10 \
  --role arn:aws:iam::${ACCOUNT_ID}:role/figureforge-lambda-role \
  --handler handler.lambda_handler \
  --zip-file fileb://worker.zip \
  --timeout 300 \
  --memory-size 1024 \
  --environment Variables="{
    DYNAMODB_TABLE=figureforge-table,
    S3_BUCKET=figureforge-images,
    FAL_AI_API_KEY=your-fal-api-key
  }"
```

### 4.3 Add SQS Trigger

```bash
aws lambda create-event-source-mapping \
  --function-name figureforge-worker \
  --event-source-arn arn:aws:sqs:us-east-1:${ACCOUNT_ID}:figureforge-image-generation \
  --batch-size 1
```

## Step 5: Deploy Frontend

### 5.1 Build Frontend

```bash
cd frontend
npm install

# Create production environment file
cat > .env.production << EOF
VITE_API_URL=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/production
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxx
VITE_COGNITO_CLIENT_ID=xxxxx
EOF

npm run build
```

### 5.2 Create S3 Bucket for Frontend

```bash
aws s3 mb s3://figureforge-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://figureforge-frontend \
  --index-document index.html \
  --error-document index.html
```

### 5.3 Deploy Frontend Files

```bash
# Upload files
aws s3 sync dist/ s3://figureforge-frontend --delete

# Set bucket policy for public access
aws s3api put-bucket-policy --bucket figureforge-frontend \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::figureforge-frontend/*"
    }]
  }'
```

### 5.4 Create CloudFront Distribution

```bash
aws cloudfront create-distribution \
  --origin-domain-name figureforge-frontend.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html \
  --comment "FigureForge Frontend CDN"
```

## Step 6: Configure Stripe Webhooks

1. Log into Stripe Dashboard
2. Go to Developers → Webhooks
3. Add endpoint: `https://your-api-url.com/api/webhooks/stripe/`
4. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook secret to your backend environment

## Step 7: Post-Deployment Tasks

### 7.1 Seed Database

```bash
cd backend
python seed_plans_dynamodb.py
```

### 7.2 Test Deployment

1. Visit your CloudFront URL
2. Create a test account
3. Generate a test image
4. Test subscription checkout

### 7.3 Set Up Monitoring

```bash
# Create CloudWatch alarms
aws cloudwatch put-metric-alarm \
  --alarm-name figureforge-api-errors \
  --alarm-description "API Gateway 5xx errors" \
  --metric-name 5XXError \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

## Custom Domain Setup

### For API

Edit `zappa_settings.json`:
```json
{
  "production": {
    "domain": "api.yourdomain.com",
    "certificate_arn": "arn:aws:acm:us-east-1:xxx:certificate/xxx"
  }
}
```

Then run:
```bash
zappa certify production
```

### For Frontend

1. Request ACM certificate for your domain
2. Create CloudFront distribution with custom domain
3. Update Route 53 records

## Troubleshooting

### Common Issues

- **CORS errors**: Check `zappa_settings.json` CORS configuration
- **502 Gateway errors**: Increase Lambda timeout or memory
- **Image generation fails**: Check worker Lambda logs in CloudWatch
- **Authentication issues**: Verify Cognito configuration

### Useful Commands

```bash
# View backend logs
zappa tail production

# Update Lambda function code
cd backend/worker
zip -r worker.zip handler.py
aws lambda update-function-code \
  --function-name figureforge-worker \
  --zip-file fileb://worker.zip

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

## Cost Optimization

- Enable S3 lifecycle rules for old images
- Use CloudFront caching headers
- Set up AWS Budget alerts
- Consider Reserved Capacity for DynamoDB if needed

## Security Checklist

- [ ] Enable AWS WAF on CloudFront and API Gateway
- [ ] Store secrets in AWS Secrets Manager
- [ ] Enable CloudTrail logging
- [ ] Review IAM permissions (least privilege)
- [ ] Enable S3 bucket versioning
- [ ] Set up backup strategy for DynamoDB