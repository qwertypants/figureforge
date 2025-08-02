# FigureForge Quick Start Guide

This guide will help you get FigureForge running locally in under 10 minutes.

## Prerequisites

- Python 3.10+
- Node.js 20+
- AWS Account (for cloud services)
- Stripe Account (for payments)
- fal.ai API Key (for image generation)

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/figureforge.git
cd figureforge
```

## Step 2: Backend Setup (5 minutes)

### 2.1 Create Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.3 Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# AWS (use local alternatives for dev)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=figureforge-dev
S3_BUCKET_NAME=figureforge-images-dev
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456/figureforge-dev

# Cognito
COGNITO_USER_POOL_ID=us-east-1_xxxxx
COGNITO_APP_CLIENT_ID=xxxxx

# External Services
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
FAL_API_KEY=xxxxx
```

### 2.4 Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

Backend is now running at `http://localhost:8000` ✅

## Step 3: Frontend Setup (3 minutes)

Open a new terminal:

### 3.1 Install Dependencies
```bash
cd frontend
npm install
```

### 3.2 Configure Environment
Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxx
VITE_COGNITO_CLIENT_ID=xxxxx
```

### 3.3 Start Development Server
```bash
npm run dev
```

Frontend is now running at `http://localhost:5173` ✅

## Step 4: Quick Test

1. Open http://localhost:5173 in your browser
2. Sign up for a new account
3. Navigate to the image generation page
4. Select filters and generate your first image!

## Local Development Tips

### Using Local Services

For faster local development without AWS:

1. **DynamoDB Local**:
   ```bash
   docker run -p 8001:8000 amazon/dynamodb-local
   ```

2. **LocalStack** (S3, SQS, etc.):
   ```bash
   docker run -p 4566:4566 localstack/localstack
   ```

3. **Stripe CLI** (for webhooks):
   ```bash
   stripe listen --forward-to localhost:8000/api/webhooks/stripe/
   ```

### Seeding Test Data

1. **Create test plans**:
   ```bash
   cd backend
   python seed_plans_dynamodb.py
   ```

2. **Create test user**:
   ```bash
   python manage.py createsuperuser
   ```

## Common Issues

### Issue: "Module not found" errors
**Solution**: Make sure your virtual environment is activated

### Issue: CORS errors in browser
**Solution**: Check that `VITE_API_URL` matches your backend URL

### Issue: Authentication fails
**Solution**: Verify Cognito credentials are correct in both frontend and backend

### Issue: Image generation fails
**Solution**: Check your fal.ai API key is valid and has credits

## Next Steps

- Read the [Architecture Overview](architecture.md)
- Check the [API Documentation](api-spec.md)
- See [Frontend Implementation](frontend-implementation.md) for UI development
- Review [Deployment Guide](deployment-checklist.md) for production setup

## Getting Help

- Check existing [documentation](../docs/)
- Review [backend README](../backend/README.md) for API details
- Open an issue on GitHub for bugs or questions