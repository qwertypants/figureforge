import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

export default function MagicLinkCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const verifyMagicLink = async () => {
      const token = searchParams.get('token');
      const email = searchParams.get('email');
      
      // Get stored session from sessionStorage
      const session = sessionStorage.getItem('magicLinkSession');
      const storedEmail = sessionStorage.getItem('magicLinkEmail');

      if (!token || !email) {
        setStatus('error');
        setErrorMessage('Invalid magic link');
        return;
      }

      // Verify email matches
      if (email !== storedEmail) {
        setStatus('error');
        setErrorMessage('Email mismatch. Please request a new magic link.');
        return;
      }

      if (!session) {
        setStatus('error');
        setErrorMessage('Session expired. Please request a new magic link.');
        return;
      }

      try {
        const response = await axios.post('/api/auth/magic-link/verify/', {
          email,
          token,
          session
        });

        if (response.data.id_token) {
          // Store the token
          localStorage.setItem('authToken', response.data.id_token);
          
          // Clear session storage
          sessionStorage.removeItem('magicLinkSession');
          sessionStorage.removeItem('magicLinkEmail');
          
          // Fetch user profile
          try {
            const userResponse = await axios.get('/api/auth/user/', {
              headers: {
                Authorization: `Bearer ${response.data.id_token}`
              }
            });
            
            setAuth({
              isAuthenticated: true,
              user: userResponse.data.user,
              subscription: userResponse.data.subscription
            });
            
            setStatus('success');
            
            // Redirect after a short delay
            setTimeout(() => {
              const redirectPath = sessionStorage.getItem('redirectAfterLogin') || '/dashboard';
              sessionStorage.removeItem('redirectAfterLogin');
              navigate(redirectPath);
            }, 1500);
          } catch (err) {
            console.error('Failed to fetch user profile:', err);
            setStatus('error');
            setErrorMessage('Failed to load user profile');
          }
        }
      } catch (err: any) {
        setStatus('error');
        setErrorMessage(err.response?.data?.error || 'Failed to verify magic link');
      }
    };

    verifyMagicLink();
  }, [searchParams, navigate, setAuth]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          {status === 'loading' && (
            <>
              <Loader2 className="mx-auto h-12 w-12 text-indigo-600 animate-spin" />
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                Verifying your magic link...
              </h2>
              <p className="mt-2 text-sm text-gray-600">
                Please wait while we sign you in
              </p>
            </>
          )}
          
          {status === 'success' && (
            <>
              <CheckCircle className="mx-auto h-12 w-12 text-green-600" />
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                Success!
              </h2>
              <p className="mt-2 text-sm text-gray-600">
                You've been signed in. Redirecting...
              </p>
            </>
          )}
          
          {status === 'error' && (
            <>
              <XCircle className="mx-auto h-12 w-12 text-red-600" />
              <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
                Verification failed
              </h2>
              <p className="mt-2 text-sm text-red-600">
                {errorMessage}
              </p>
              <button
                onClick={() => navigate('/login/magic-link')}
                className="mt-6 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Request new magic link
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}