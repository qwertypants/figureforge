# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FigureForge is an AI-powered figure drawing reference generator web application for hobbyist artists. It generates SFW human figure reference images using AI with subscription management.

## Tech Stack

- **Frontend**: React SPA with Vite, TypeScript, Tailwind CSS, Zustand state management
- **Backend**: Django REST Framework on AWS Lambda (via Zappa)
- **Database**: DynamoDB (single-table design) + SQLite for local development
- **Authentication**: AWS Cognito + Magic Link authentication
- **Storage**: AWS S3 + CloudFront CDN (with signed URLs)
- **Queue**: AWS SQS + Worker Lambda
- **Image Generation**: fal.ai API
- **Payments**: Stripe (with webhook support)

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

### Frontend (React/Vite/TypeScript)
```bash
cd frontend

# Development
npm run dev              # Start development server
npm run lint             # Run ESLint
npm run build            # Build for production  
npm run preview          # Preview production build

# Note: No test script is currently configured in package.json
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
1. **Authentication Flow**: 
   - Standard: Cognito JWT tokens → Django CognitoAuthMiddleware → DynamoDB user records
   - Magic Link: Email request → Cognito Lambda → Email with code → Verification endpoint
2. **Image Generation**: Frontend request → Django API → SQS queue → Worker Lambda → fal.ai → S3 storage → CloudFront signed URLs
3. **Subscription Management**: Stripe webhooks → Django webhook handler → DynamoDB updates
4. **API Structure**: Modular views organized by feature (auth, images, subscriptions, webhooks)

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
- Frontend: No test framework currently configured
- Test files exist in `/backend/api/tests/` for core utilities
- Always test authentication flows and payment integrations

## Environment Setup

### Required Environment Variables
Backend (`.env`):
- Django: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- Services: `DYNAMODB_TABLE`, `S3_BUCKET`, `SQS_QUEUE_URL`, `COGNITO_USER_POOL_ID`
- External: `STRIPE_SECRET_KEY`, `FAL_AI_API_KEY`
- URLs: `FRONTEND_URL`, `BACKEND_URL`

Frontend (`.env` or environment variables):
- `VITE_API_URL` - Backend API endpoint
- `VITE_STRIPE_PUBLISHABLE_KEY` - Stripe public key
- `VITE_COGNITO_USER_POOL_ID` - Cognito user pool ID
- `VITE_COGNITO_CLIENT_ID` - Cognito client ID
- `VITE_COGNITO_DOMAIN` - Cognito domain

## Subscription Tiers
- **Hobby**: $9.99/month - 50 images
- **Pro**: $24.99/month - 300 images  
- **Studio**: $99.99/month - 2000 images

## Important Files
- `/backend/api/urls.py` - API URL routing configuration
- `/backend/api/views/` - Modular API views by feature
- `/backend/worker/handler.py` - AWS Lambda handler for image generation
- `/backend/figureforge/settings.py` - Django settings with environment variables
- `/frontend/src/App.tsx` - Main React TypeScript component
- `/frontend/src/stores/` - Zustand state management stores
- `/frontend/src/api/` - API client modules
- `/docs/` - Comprehensive documentation (14 files covering all aspects)

## Additional Project Details

### Python Version
- Backend uses Python 3.10 (as configured in zappa_settings.json)

### Key Dependencies
- Backend: Django 5.2.4, DRF 3.16.0, Zappa 0.60.2, Boto3, Stripe
- Frontend: React 19, Vite 5.4, TypeScript 5.9, Tailwind CSS 4.1, Zustand 5.0

### Deployment Configuration
- Development: 512MB memory, 30s timeout, CORS enabled
- Production: 1024MB memory, 60s timeout, keep-warm enabled
- S3 bucket for deployments: `figureforge-zappa-deployments`

### Feature Flags (in settings.py)
- `public_gallery`: True
- `social_login`: False  
- `admin_moderation`: True

### Image Generation Settings
- `MAX_BATCH_SIZE`: 4
- `IMAGE_GENERATION_TIMEOUT`: 300 seconds (5 minutes)
- `SIGNED_URL_TTL`: 600 seconds (10 minutes)