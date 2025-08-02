# FigureForge

AI-powered figure drawing reference generator with subscription management. A web application for generating SFW human figure reference images for hobbyist artists using AI.

## Project Structure

```
figureforge/
├── backend/          # Django REST API
│   ├── api/          # API app with views, models, etc.
│   ├── figureforge/  # Django project settings
│   ├── worker/       # Lambda worker for image generation
│   ├── manage.py     # Django management script
│   └── requirements.txt
├── frontend/         # React SPA with TypeScript
│   ├── src/          # React source code
│   │   ├── api/      # API client modules
│   │   ├── components/ # React components
│   │   ├── pages/    # Page components
│   │   ├── stores/   # Zustand state stores
│   │   ├── types/    # TypeScript types
│   │   └── App.tsx   # Main app component
│   ├── public/       # Static assets
│   └── package.json
└── docs/             # Project documentation
```

## Tech Stack

- **Frontend**: React SPA with Vite, TypeScript, Tailwind CSS, Zustand
- **Backend**: Django REST Framework on AWS Lambda
- **Database**: DynamoDB (single-table design)
- **Authentication**: Amazon Cognito + Magic Link
- **Storage**: AWS S3 + CloudFront CDN
- **Queue**: AWS SQS + Worker Lambda
- **Image Generation**: fal.ai API
- **Payments**: Stripe

## Features

- **AI Image Generation**: Generate figure references using fal.ai models (FLUX, Stable Diffusion)
- **Customizable Filters**: Body type, pose, lighting, clothing, background
- **Subscription Tiers**: Hobby ($9.99), Pro ($24.99), Studio ($99.99)
- **User Gallery**: Save and organize generated images with tags
- **Public Gallery**: Browse community-generated references
- **Secure Authentication**: AWS Cognito with password and magic link options
- **Responsive Design**: Mobile-first React interface

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 20+
- AWS Account
- Stripe Account
- fal.ai API Key

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/figureforge.git
   cd figureforge
   ```

2. Set up the backend:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your credentials
   python manage.py migrate
   python manage.py runserver
   ```

3. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

4. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## Configuration

See `backend/.env.example` for all required environment variables:

- **AWS**: DynamoDB, S3, SQS, Cognito configuration
- **Stripe**: API keys and webhook secrets
- **fal.ai**: API key for image generation
- **Django**: Secret key and settings

## API Documentation

### Key Endpoints

- **Auth**: `/api/auth/` - User authentication and profile
- **Images**: `/api/images/` - Image generation and management
- **Subscriptions**: `/api/subscriptions/` - Billing and plans
- **Webhooks**: `/api/webhooks/` - External service integrations

See `backend/README.md` for complete API documentation.

## Deployment

This guide covers deploying FigureForge to AWS using Lambda, S3, CloudFront, and other AWS services.

### Prerequisites

1. **AWS CLI configured**: Run `aws configure` with your credentials
2. **Python environment**: Python 3.10+ with virtualenv
3. **Node.js**: Version 20+ for frontend build
4. **Domain name** (optional): For custom domains

### Step 1: Deploy Backend with Zappa

1. **Activate virtual environment and install dependencies**:
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create S3 bucket for Zappa deployments**:
   ```bash
   aws s3 mb s3://figureforge-zappa-deployments --region us-east-1
   ```

3. **Deploy to development environment**:
   ```bash
   zappa deploy dev
   ```
   
   Note the API Gateway URL provided after deployment (e.g., `https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev`)

4. **For production deployment**:
   ```bash
   zappa deploy production
   ```

5. **Update deployed function**:
   ```bash
   zappa update dev  # or production
   ```

### Step 2: Set Up AWS Services

1. **Create DynamoDB Table**:
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

2. **Create S3 Bucket for Images**:
   ```bash
   aws s3 mb s3://figureforge-images --region us-east-1
   
   # Enable public read for images
   aws s3api put-bucket-policy --bucket figureforge-images \
     --policy file://s3-bucket-policy.json
   ```

3. **Create SQS Queue**:
   ```bash
   aws sqs create-queue \
     --queue-name figureforge-image-generation \
     --region us-east-1
   ```

4. **Set Up Cognito User Pool**:
   ```bash
   aws cognito-idp create-user-pool \
     --pool-name figureforge-users \
     --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true}" \
     --auto-verified-attributes email \
     --region us-east-1
   ```

5. **Configure Magic Link Authentication (Optional)**:
   
   If you want to enable passwordless authentication via magic links:
   
   a. **Deploy Cognito Lambda Triggers**:
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
   
   b. **Configure SES for Email Sending**:
   ```bash
   # Verify your sender email address
   aws ses verify-email-identity --email-address noreply@yourdomain.com
   
   # For production, request SES production access to send to any email
   # By default, SES is in sandbox mode and can only send to verified emails
   ```
   
   c. **Update Cognito App Client Settings**:
   ```bash
   # Get your User Pool ID and App Client ID
   USER_POOL_ID=$(aws cognito-idp list-user-pools --max-results 10 \
     --query "UserPools[?Name=='figureforge-users'].Id" --output text)
   
   APP_CLIENT_ID=$(aws cognito-idp list-user-pool-clients \
     --user-pool-id $USER_POOL_ID \
     --query "UserPoolClients[0].ClientId" --output text)
   
   # Update app client to support CUSTOM_AUTH flow
   aws cognito-idp update-user-pool-client \
     --user-pool-id $USER_POOL_ID \
     --client-id $APP_CLIENT_ID \
     --explicit-auth-flows ALLOW_CUSTOM_AUTH ALLOW_USER_SRP_AUTH ALLOW_REFRESH_TOKEN_AUTH
   ```
   
   d. **Update Backend Environment Variables**:
   Add these to your `.env` file:
   ```
   COGNITO_REGION=us-east-1
   COGNITO_USER_POOL_ID=your-user-pool-id
   COGNITO_CLIENT_ID=your-app-client-id
   ```
   
   e. **Frontend Configuration**:
   The magic link routes are already configured. Users can access:
   - `/login/magic-link` - Request a magic link
   - `/auth/magic-link` - Callback URL for magic link verification

### Step 3: Deploy Worker Lambda

Before creating the Lambda function, you need to set up an IAM role with the necessary permissions.

1. **Create IAM role for Lambda execution**:
   ```bash
   # Create trust policy file
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
   
   # Create the role
   aws iam create-role \
     --role-name figureforge-lambda-role \
     --assume-role-policy-document file://lambda-trust-policy.json
   
   # Attach basic Lambda execution policy
   aws iam attach-role-policy \
     --role-name figureforge-lambda-role \
     --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
   
   # Create and attach custom policy for your services
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

2. **Package worker function with dependencies**:
   ```bash
   cd backend/worker
   
   # Create a deployment package directory
   mkdir package
   
   # Install dependencies into package directory
   pip install -r requirements.txt -t package/
   
   # Copy your handler code
   cp handler.py package/
   
   # Create deployment zip
   cd package
   zip -r ../worker.zip .
   cd ..
   ```

3. **Create Lambda function**:
   ```bash
   # Get your AWS account ID
   ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
   
   # Create the Lambda function
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

4. **Add SQS trigger**:
   ```bash
   aws lambda create-event-source-mapping \
     --function-name figureforge-worker \
     --event-source-arn arn:aws:sqs:us-east-1:${ACCOUNT_ID}:queue/figureforge-image-generation \
     --batch-size 1
   ```

5. **Update Lambda function** (when you make changes):
   ```bash
   # Repackage and update
   cd backend/worker
   zip -r worker.zip handler.py
   aws lambda update-function-code \
     --function-name figureforge-worker \
     --zip-file fileb://worker.zip
   ```

**Alternative: Using AWS Console**

If you prefer using the AWS Console:
1. Go to AWS Lambda service
2. Click "Create function"
3. Choose "Author from scratch"
4. Set function name: `figureforge-worker`
5. Runtime: Python 3.10
6. Under "Permissions", create a new role with basic Lambda permissions
7. After creation, add the necessary policies to the role in IAM
8. Upload your zip file in the "Code" section
9. Add environment variables in "Configuration" > "Environment variables"
10. Add SQS trigger in "Configuration" > "Triggers"

### Step 4: Deploy Frontend to S3/CloudFront

1. **Build frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Create S3 bucket for frontend**:
   ```bash
   aws s3 mb s3://figureforge-frontend --region us-east-1
   
   # Enable static website hosting
   aws s3 website s3://figureforge-frontend \
     --index-document index.html \
     --error-document index.html
   ```

3. **Deploy frontend files**:
   ```bash
   aws s3 sync dist/ s3://figureforge-frontend --delete
   
   # Set public read permissions
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

4. **Create CloudFront distribution**:
   ```bash
   aws cloudfront create-distribution \
     --origin-domain-name figureforge-frontend.s3-website-us-east-1.amazonaws.com \
     --default-root-object index.html \
     --comment "FigureForge Frontend CDN"
   ```

### Step 5: Configure Environment Variables

1. **Update backend environment variables**:
   ```bash
   cd backend
   # Edit .env file with your AWS resource IDs/ARNs
   ```

2. **Update Zappa settings with environment variables**:
   ```bash
   zappa update dev -s zappa_settings.json
   ```

3. **Update frontend API endpoint**:
   Create `.env.production` in frontend directory:
   ```
   VITE_API_URL=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/dev
   ```

### Step 6: Set Up Custom Domain (Optional)

1. **For API (backend)**:
   ```bash
   # In zappa_settings.json, add:
   "domain": "api.yourdomain.com",
   "certificate_arn": "arn:aws:acm:us-east-1:YOUR_ACCOUNT_ID:certificate/..."
   
   # Then run:
   zappa certify production
   ```

2. **For Frontend**:
   - Create CloudFront distribution with custom domain
   - Add Route 53 records pointing to CloudFront

### Step 7: Post-Deployment Tasks

1. **Run database migrations**:
   ```bash
   zappa manage production migrate
   ```

2. **Create admin user**:
   ```bash
   zappa manage production createsuperuser
   ```

3. **Test the deployment**:
   - Visit your CloudFront URL or custom domain
   - Test user registration and login
   - Generate a test image
   - Verify Stripe webhooks

### Monitoring and Logs

- **Backend logs**: `zappa tail dev`
- **Worker logs**: CloudWatch Logs for Lambda function
- **Frontend errors**: CloudFront logs in S3

### Cost Optimization

- Use Lambda reserved concurrency for predictable traffic
- Enable S3 lifecycle policies for old images
- Set up CloudFront caching headers
- Monitor DynamoDB consumed capacity

### Security Best Practices

1. **Enable AWS WAF** on CloudFront and API Gateway
2. **Use Parameter Store** or Secrets Manager for sensitive data
3. **Enable CloudTrail** for audit logging
4. **Set up budget alerts** in AWS Billing

### Troubleshooting

- **CORS errors**: Check `zappa_settings.json` CORS configuration
- **502 errors**: Increase Lambda timeout or memory
- **Image generation failures**: Check SQS dead letter queue
- **Authentication issues**: Verify Cognito app client settings

## Architecture

- **Serverless Backend**: Django on AWS Lambda via Zappa
- **NoSQL Database**: DynamoDB with single-table design
- **Async Processing**: SQS queue with Lambda workers
- **CDN**: CloudFront for static assets and images
- **Authentication**: JWT tokens via AWS Cognito

## License

Private - All rights reserved
