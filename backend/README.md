# FigureForge Backend

Django REST API backend for FigureForge - AI-powered figure drawing reference generator.

## Architecture

- **Django REST Framework** for API endpoints
- **AWS DynamoDB** for data storage (single-table design)
- **AWS Cognito** for authentication
- **AWS S3** for image storage
- **AWS SQS** for job queue
- **AWS Lambda** for serverless deployment (via Zappa)
- **Stripe** for subscription billing
- **fal.ai** for AI image generation

## Setup

### Prerequisites

- Python 3.10+
- AWS CLI configured with credentials
- Virtual environment

### Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

### Environment Variables

Key environment variables needed:

- `SECRET_KEY` - Django secret key
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `DYNAMODB_TABLE_NAME` - DynamoDB table name
- `S3_BUCKET_NAME` - S3 bucket for images
- `SQS_QUEUE_URL` - SQS queue URL
- `COGNITO_USER_POOL_ID` - Cognito user pool ID
- `COGNITO_APP_CLIENT_ID` - Cognito app client ID
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- `FAL_API_KEY` - fal.ai API key

### Local Development

1. Run migrations (creates local SQLite for Django admin):
```bash
python manage.py migrate
```

2. Create superuser (optional):
```bash
python manage.py createsuperuser
```

3. Run development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

### API Endpoints

#### Authentication
- `GET /api/auth/user/` - Get current user
- `PUT /api/auth/user/update/` - Update user profile
- `GET /api/auth/user/stats/` - Get user statistics
- `POST /api/auth/verify/` - Verify JWT token
- `DELETE /api/auth/delete/` - Delete account

#### Image Generation
- `POST /api/images/generate/` - Create generation job
- `GET /api/images/job/{job_id}/` - Get job status
- `GET /api/images/user/` - Get user's images
- `GET /api/images/gallery/` - Get public gallery
- `GET /api/images/{image_id}/` - Get image details
- `DELETE /api/images/{image_id}/delete/` - Delete image
- `PUT /api/images/{image_id}/update/` - Update image metadata
- `GET /api/images/models/` - Get available models

#### Subscriptions
- `GET /api/subscriptions/plans/` - Get subscription plans
- `GET /api/subscriptions/current/` - Get current subscription
- `POST /api/subscriptions/checkout/` - Create checkout session
- `POST /api/subscriptions/portal/` - Create billing portal session
- `POST /api/subscriptions/cancel/` - Cancel subscription
- `POST /api/subscriptions/reactivate/` - Reactivate subscription

#### Webhooks
- `POST /api/webhooks/stripe/` - Stripe webhook handler
- `GET /api/webhooks/health/` - Health check

### Deployment

#### Deploy with Zappa

1. Configure AWS credentials:
```bash
aws configure
```

2. Deploy to development:
```bash
zappa deploy dev
```

3. Update deployment:
```bash
zappa update dev
```

4. View logs:
```bash
zappa tail dev
```

#### Deploy Worker Lambda

The worker Lambda processes image generation jobs from SQS.

1. Package worker:
```bash
cd worker
pip install -r requirements.txt -t .
zip -r worker.zip .
```

2. Deploy to AWS Lambda and configure SQS trigger.

### Testing

The tests are written using pytest. To run them:

#### Prerequisites
```bash
pip install pytest pytest-cov
```

#### Running Tests

**Run all tests in api/core**:
```bash
export DJANGO_SETTINGS_MODULE=figureforge.settings
pytest api/core/tests/ -v
```

**Run a specific test file**:
```bash
export DJANGO_SETTINGS_MODULE=figureforge.settings
pytest api/core/tests/test_dynamodb_utils.py -v
```

**Run tests with coverage**:
```bash
export DJANGO_SETTINGS_MODULE=figureforge.settings
pytest api/core/tests/ --cov=api.core -v
```

**Run a specific test class**:
```bash
export DJANGO_SETTINGS_MODULE=figureforge.settings
pytest api/core/tests/test_dynamodb_utils.py::TestDynamoDBClient -v
```

**Run a specific test method**:
```bash
export DJANGO_SETTINGS_MODULE=figureforge.settings
pytest api/core/tests/test_dynamodb_utils.py::TestDynamoDBClient::test_serialize_item_converts_floats_to_decimal -v
```

#### Alternative: Using Django's test runner

If you prefer Django's test runner (though it won't run the pytest-style tests):
```bash
python manage.py test api
```

#### Test Structure

Tests are located in `api/core/tests/`:
- `test_dynamodb_utils.py` - Tests for DynamoDB operations
- `test_s3_utils.py` - Tests for S3 and CloudFront utilities
- `test_sqs_utils.py` - Tests for SQS queue operations
- `test_fal_client.py` - Tests for fal.ai API client
- `test_stripe_client.py` - Tests for Stripe integration

**Note**: Make sure you have the required environment variables set (or mocked) before running tests.

### Project Structure

```
backend/
├── api/                    # Main API app
│   ├── core/              # Core utilities
│   │   ├── dynamodb_utils.py
│   │   ├── s3_utils.py
│   │   ├── sqs_utils.py
│   │   ├── fal_client.py
│   │   └── stripe_client.py
│   ├── middleware/        # Custom middleware
│   │   └── cognito_auth.py
│   ├── views/            # API views
│   │   ├── auth.py
│   │   ├── images.py
│   │   ├── subscriptions.py
│   │   └── webhooks.py
│   └── urls.py           # API routes
├── figureforge/          # Django project settings
├── worker/               # Lambda worker for jobs
├── manage.py
├── requirements.txt
└── zappa_settings.json
```

## Development Notes

- All data is stored in DynamoDB using single-table design
- Authentication is handled by AWS Cognito
- Images are stored in S3 with signed URLs
- Job processing is async via SQS and Lambda
- Stripe webhooks update subscription status
