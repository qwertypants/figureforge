import { useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from 'react-oidc-context'
import { Mail } from 'lucide-react'
import useAuthStore from '../stores/authStore'
import { LocationState } from '../types/types'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const auth = useAuth()
  const { error } = useAuthStore()
  
  const state = location.state as LocationState
  
  // Redirect if already authenticated
  useEffect(() => {
    if (auth.isAuthenticated) {
      const from = state?.from?.pathname || '/generate'
      navigate(from, { replace: true })
    }
  }, [auth.isAuthenticated, navigate, state])
  
  const handleLogin = () => {
    // Store the intended destination
    const from = state?.from?.pathname || '/generate'
    sessionStorage.setItem('authReturnTo', from)
    
    // Initiate the sign-in redirect
    auth.signinRedirect()
  }
  
  if (auth.isLoading) {
    return <div className="text-center">Loading...</div>
  }
  
  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-3xl font-bold text-center mb-8">Sign In</h2>
      
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {auth.error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {auth.error.message}
        </div>
      )}
      
      <div className="space-y-6">
        <button
          onClick={handleLogin}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Sign In with Cognito
        </button>
        
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or continue with</span>
          </div>
        </div>
        
        <Link
          to="/login/magic-link"
          className="w-full flex items-center justify-center gap-2 bg-white text-gray-700 py-3 px-4 rounded-md border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
        >
          <Mail className="h-5 w-5" />
          Sign in with Magic Link
        </Link>
        
        <div className="text-center text-sm text-gray-600">
          We'll send you a secure link to sign in without a password
        </div>
      </div>
      
      <div className="mt-6 text-center text-sm">
        Don't have an account?{' '}
        <Link to="/signup" className="text-blue-600 hover:text-blue-500">
          Sign up
        </Link>
      </div>
    </div>
  )
}

export default Login