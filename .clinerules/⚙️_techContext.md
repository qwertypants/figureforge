# ⚙️ Technical Context

## SPARC Development Methodology

The project follows the SPARC methodology for structured development:

1. **Specification**: Define requirements, constraints, and acceptance criteria
2. **Pseudocode**: Develop high-level logic with TDD anchors
3. **Architecture**: Design modular components with clear interfaces
4. **Refinement**: Implement with TDD, debugging, and optimization
5. **Completion**: Integrate, document, test, and verify against criteria

### Technical Requirements
- Files must not exceed 500 lines
- Functions must follow single responsibility principle
- No hardcoded environment variables or secrets
- All code must include proper error handling
- Modular architecture with clear component boundaries
- Comprehensive test coverage for critical functionality

## Technology Stack

### Frontend
- React (SPA)
- Tailwind CSS (UI component and styling)
- Zustand (State management)
- Tailwind CSS utility-first approach
- Vite (Build tool)

### Backend
- Python (Django REST Framework)
- REST API architecture
- DynamoDB (single-table design)
- Amazon Cognito (authentication)
- AWS S3/CloudFront for caching & CDN

### Infrastructure
- AWS (S3, CloudFront, API Gateway, Lambda, DynamoDB, Cognito, SQS)
- GitHub Actions for CI/CD
- Docker (for containerization during development)
- AWS CloudWatch (monitoring)
- CloudWatch Logs

## Development Environment

### Required Tools
- Python 3.11
- Node.js 20.x and npm
- AWS CLI (latest)

### Setup Instructions
```bash
npm install
pip install -r requirements.txt
aws configure
```

### Local Development Workflow
1. Run `npm run dev` in frontend
2. Run `python manage.py runserver` in backend
3. Test via local API Gateway mock or direct backend endpoints

## External Dependencies

### APIs
- fal.ai: Image generation
- Stripe: Subscription billing

### Third-party Services
- Amazon Cognito: Authentication & user management
- AWS CloudFront: CDN

### Libraries and Frameworks
- Django REST Framework: API endpoints
- React Router: SPA routing

## Technical Constraints

### Performance Requirements
- Must support mobile-first responsive rendering
- Generate up to 4 images per batch within cost constraints

### Security Requirements
- No hardcoded secrets, credentials, or environment variables
- All user inputs must be validated and sanitized
- Proper error handling to prevent information leakage
- Secure coding practices following OWASP guidelines
- Regular security audits of dependencies

### Compatibility Requirements
- [Requirement 1]
- [Requirement 2]


## Testing Strategy

### SPARC Testing Approach
- Test-Driven Development (TDD) for all new features
- Tests written during Pseudocode phase before implementation
- Comprehensive test coverage for critical functionality
- Automated testing integrated into CI/CD pipeline

### Unit Testing
- Test individual components in isolation
- Mock dependencies for pure unit testing
- Aim for >80% code coverage on critical paths
- Focus on edge cases and error handling

### Integration Testing
- Test component interactions and interfaces
- Verify correct data flow between modules
- Test API contracts and boundaries
- Ensure proper error propagation

### End-to-End Testing
- Cypress for end-to-end testing
- Test user signup, payment, image generation, and gallery browsing

## Deployment Process

### Environments
- Development: Local Docker-based setup with mocked AWS services
- Staging: AWS environment for testing new features
- Production: AWS environment serving live users

### Deployment Steps
1. Push changes to main branch triggers CI/CD
2. Automated tests and lint checks run
3. Deploy backend via Zappa and frontend to S3/CloudFront

### Rollback Procedure
1. Revert to previous stable deployment using S3 versioning and Lambda alias rollback
2. Invalidate CloudFront cache
3. Run smoke tests


