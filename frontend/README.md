# FigureForge Frontend

This is the frontend application for FigureForge - an AI-powered figure drawing reference generator for hobbyist artists.

## Tech Stack

- **React 19** with TypeScript
- **Vite 5.4** for build tooling
- **Tailwind CSS 4.1** for styling
- **Zustand 5.0** for state management
- **React Router 7.7** for routing
- **Axios** for API calls
- **Stripe.js** for payment processing
- **AWS Cognito** for authentication

## Prerequisites

- Node.js 18+ and npm
- Backend API running (see backend README)

## Setup

1. Install dependencies:

```bash
npm install
```

2. Create a `.env` file based on the example:

```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:

```
VITE_API_URL=http://localhost:8000/api
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
VITE_COGNITO_CLIENT_ID=your-cognito-client-id
VITE_COGNITO_DOMAIN=your-cognito-domain
```

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at http://localhost:5173

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── api/          # API client modules
│   ├── auth.ts   # Authentication API calls
│   ├── billing.ts # Subscription/billing API calls
│   ├── config.ts # API configuration
│   └── images.ts # Image generation API calls
├── components/   # Reusable UI components
│   ├── ImageCard.tsx
│   └── Layout.tsx
├── pages/        # Page components
│   ├── Account.tsx
│   ├── AuthCallback.tsx
│   ├── Generate.tsx
│   ├── Home.tsx
│   ├── Login.tsx
│   ├── MagicLinkCallback.tsx
│   ├── MagicLinkLogin.tsx
│   ├── MyImages.tsx
│   ├── Pricing.tsx
│   ├── PublicGallery.tsx
│   └── SignUp.tsx
├── stores/       # Zustand state stores
│   ├── authStore.ts
│   └── imageStore.ts
├── types/        # TypeScript type definitions
│   └── types.ts
├── utils/        # Utility functions
│   ├── auth.ts
│   └── oidcAuth.ts
├── App.tsx       # Main app component
├── main.tsx      # App entry point
└── index.css     # Global styles
```

## Key Features

- **Authentication**: AWS Cognito integration with magic link support
- **Image Generation**: AI-powered figure drawing reference generation
- **Subscription Management**: Stripe integration for subscription tiers
- **Image Gallery**: Personal and public galleries
- **Responsive Design**: Mobile-friendly interface

## Authentication Flow

The app supports two authentication methods:

1. **Standard Cognito Auth**: Traditional email/password login
2. **Magic Link**: Passwordless email authentication

## State Management

Global state is managed using Zustand stores:

- `authStore`: User authentication state
- `imageStore`: Generated images and gallery state

## API Integration

All API calls go through the modules in `src/api/`:

- Axios interceptors handle authentication headers
- Base URL is configured via environment variable
- Error handling is centralized

## Deployment

Build the production bundle:

```bash
npm run build
```

The built files will be in the `dist/` directory, ready to be deployed to your hosting service.

## Environment Variables

| Variable                      | Description              | Example                     |
| ----------------------------- | ------------------------ | --------------------------- |
| `VITE_API_URL`                | Backend API URL          | `http://localhost:8000/api` |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key   | `pk_test_...`               |
| `VITE_COGNITO_USER_POOL_ID`   | AWS Cognito user pool ID | `us-east-1_...`             |
| `VITE_COGNITO_CLIENT_ID`      | Cognito app client ID    | `abc123...`                 |
| `VITE_COGNITO_DOMAIN`         | Cognito hosted UI domain | `figureforge.auth...`       |

## Contributing

1. Follow the existing code style
2. Use TypeScript for all new code
3. Keep components small and focused
4. Write meaningful commit messages

## License

See the main project README for license information.
