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
- **Customizable Filters**: 8 dimensions - pose, body region, style, clothing, lighting, camera, theme, background
- **Subscription Tiers**: Hobby ($9.99/50 images), Pro ($24.99/300 images), Studio ($99.99/2000 images)
- **User Gallery**: Save and organize generated images with auto-tagging
- **Public Gallery**: Browse community-generated references
- **Secure Authentication**: AWS Cognito with password and magic link options
- **Responsive Design**: Mobile-first React interface
- **Moderation System**: Community flagging with AI-assisted review

## Getting Started

See the [Quick Start Guide](docs/quickstart.md) to get FigureForge running locally in under 10 minutes.

### Prerequisites

- Python 3.10+
- Node.js 20+
- AWS Account
- Stripe Account
- fal.ai API Key

### Quick Overview

1. Clone the repository
2. Set up backend with Django
3. Set up frontend with React
4. Configure environment variables
5. Start development servers

Full instructions in the [Quick Start Guide](docs/quickstart.md).

## Configuration

### Backend Environment Variables
See `backend/.env.example` for all required variables:
- **AWS**: DynamoDB, S3, SQS, Cognito configuration
- **Stripe**: API keys and webhook secrets
- **fal.ai**: API key for image generation
- **Django**: Secret key and settings

### Frontend Environment Variables
Create `frontend/.env` with:
```
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_COGNITO_USER_POOL_ID=us-east-1_...
VITE_COGNITO_CLIENT_ID=...
```

## Documentation

- **Quick Start**: [`docs/quickstart.md`](docs/quickstart.md) - Get running in 10 minutes
- **API Specification**: [`docs/api-spec.md`](docs/api-spec.md) - Complete API documentation
- **Architecture**: [`docs/architecture.md`](docs/architecture.md) - System design overview
- **Frontend Progress**: [`docs/frontend-implementation.md`](docs/frontend-implementation.md) - UI implementation tracking
- **Deployment Guide**: [`docs/deployment-guide.md`](docs/deployment-guide.md) - Production deployment instructions
- **All Documentation**: [`docs/`](docs/) - Complete project documentation

## Deployment

For production deployment to AWS, see the comprehensive [Deployment Guide](docs/deployment-guide.md) which covers:

- Backend deployment with Zappa
- AWS services setup (DynamoDB, S3, SQS, Cognito)
- Worker Lambda configuration
- Frontend deployment to CloudFront
- Custom domain setup
- Monitoring and security

## Architecture

- **Serverless Backend**: Django on AWS Lambda via Zappa
- **NoSQL Database**: DynamoDB with single-table design
- **Async Processing**: SQS queue with Lambda workers
- **CDN**: CloudFront for static assets and images
- **Authentication**: JWT tokens via AWS Cognito

## Contributing

This is a private project. Please contact the repository owner for contribution guidelines.

## License

Private - All rights reserved