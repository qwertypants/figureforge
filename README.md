# FigureForge

AI-powered figure drawing reference generator with subscription management. A web application for generating SFW human figure reference images for hobbyist artists using AI.

## Project Structure

```
figureforge/
├── backend/          # Django REST API
│   ├── figureforge/  # Django project settings
│   ├── manage.py     # Django management script
│   └── requirements.txt
├── frontend/         # React SPA
│   ├── src/          # React source code
│   ├── public/       # Static assets
│   └── package.json
└── docs/             # Project documentation
```

## Tech Stack

- **Frontend**: React SPA with Vite, Tailwind CSS, Zustand
- **Backend**: Django REST Framework on AWS Lambda
- **Database**: DynamoDB (single-table design)
- **Authentication**: Amazon Cognito
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
- **Secure Authentication**: AWS Cognito integration
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

### Backend (AWS Lambda)
```bash
cd backend
zappa deploy production
```

### Frontend (S3 + CloudFront)
```bash
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket-name
```

### Worker Lambda
Deploy `backend/worker/handler.py` as a Lambda function with SQS trigger.

## Architecture

- **Serverless Backend**: Django on AWS Lambda via Zappa
- **NoSQL Database**: DynamoDB with single-table design
- **Async Processing**: SQS queue with Lambda workers
- **CDN**: CloudFront for static assets and images
- **Authentication**: JWT tokens via AWS Cognito

## License

Private - All rights reserved
