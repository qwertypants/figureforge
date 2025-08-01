# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FigureForge is an AI-powered figure drawing reference generator web application for hobbyist artists. It generates SFW human figure reference images using AI with subscription management.

## Tech Stack

- **Frontend**: React SPA with Vite, Tailwind CSS, Zustand state management
- **Backend**: Django REST Framework on AWS Lambda (via Zappa)
- **Database**: DynamoDB (single-table design)
- **Authentication**: AWS Cognito
- **Storage**: AWS S3 + CloudFront CDN
- **Queue**: AWS SQS + Worker Lambda
- **Image Generation**: fal.ai API
- **Payments**: Stripe

## Common Development Commands

### Backend (Django)
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Development
python manage.py runserver
python manage.py test
python manage.py makemigrations
python manage.py migrate

# Deployment
zappa update dev         # Update development environment
zappa deploy production  # Deploy to production
```

### Frontend (React/Vite)
```bash
cd frontend

# Development
npm run dev              # Start development server
npm run lint             # Run ESLint
npm run build            # Build for production
npm run preview          # Preview production build

# Testing
npm test                 # Run tests (if configured)
```

## Architecture Overview

### Backend Architecture
- **Django Apps**: API endpoints served via AWS Lambda
- **Worker Lambda**: Separate function for async image generation tasks
- **DynamoDB**: Single-table design with composite keys for all entities
- **SQS Queue**: Decouples image generation requests from processing

### Frontend Architecture
- **React Components**: Modular UI components in `/frontend/src/components/`
- **State Management**: Zustand stores for global state
- **API Integration**: Axios for HTTP requests to Django backend
- **Routing**: React Router for SPA navigation

### Key Patterns
1. **Authentication Flow**: Cognito JWT tokens → Django authentication → DynamoDB user records
2. **Image Generation**: Frontend request → Django API → SQS queue → Worker Lambda → fal.ai → S3 storage
3. **Subscription Management**: Stripe webhooks → Django handler → DynamoDB updates

## Development Guidelines

### Code Standards
- Maximum file size: 500 lines
- Maximum function size: 50 lines
- Follow SPARC methodology for complex features
- Use TDD approach for critical functionality
- No hardcoded secrets or credentials

### Security Requirements
- All user inputs must be validated and sanitized
- Authentication required for all API endpoints except public galleries
- CORS properly configured for frontend domain only
- Secrets stored in environment variables or AWS Secrets Manager

### Testing
- Backend: Django test framework for unit and integration tests
- Frontend: Jest/React Testing Library (if configured)
- Always test authentication flows and payment integrations

## Environment Setup

### Required Environment Variables
Backend (`.env`):
- Django: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- Services: `DYNAMODB_TABLE`, `S3_BUCKET`, `SQS_QUEUE_URL`, `COGNITO_USER_POOL_ID`
- External: `STRIPE_SECRET_KEY`, `FAL_AI_API_KEY`
- URLs: `FRONTEND_URL`, `BACKEND_URL`

Frontend:
- Configure API endpoint in environment-specific config files

## Subscription Tiers
- **Hobby**: $9.99/month - 50 images
- **Pro**: $24.99/month - 300 images  
- **Studio**: $99.99/month - 2000 images

## Important Files
- `/backend/api/views.py` - Main API endpoints
- `/backend/worker/handler.py` - Image generation worker
- `/frontend/src/App.jsx` - Main React component
- `/docs/architecture.md` - Detailed system architecture
- `/docs/api-spec.md` - API endpoint specifications