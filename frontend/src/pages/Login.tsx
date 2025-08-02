import { useState, useEffect, FormEvent } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Mail, Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import useAuthStore from '../stores/authStore'
import { LocationState } from '../types/types'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { signIn, isAuthenticated, isLoading } = useAuth()
  const { error, setError } = useAuthStore()
  
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const state = location.state as LocationState
  
  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = state?.from?.pathname || '/generate'
      navigate(from, { replace: true })
    }
  }, [isAuthenticated, navigate, state])
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    
    try {
      await signIn(email, password)
      const from = state?.from?.pathname || '/generate'
      navigate(from, { replace: true })
    } catch (err: any) {
      if (err.code === 'UserNotConfirmedException') {
        setError('Please verify your email before signing in. Check your inbox for a verification link.')
      } else if (err.code === 'NotAuthorizedException') {
        setError('Invalid email or password')
      } else if (err.code === 'UserNotFoundException') {
        setError('No account found with this email')
      } else {
        setError(err.message || 'Failed to sign in')
      }
    } finally {
      setIsSubmitting(false)
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-3xl font-bold text-center mb-8">Sign In</h2>
      
      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter your email"
          />
        </div>
        
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password
          </label>
          <div className="mt-1 relative">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your password"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <Link
            to="/forgot-password"
            className="text-sm text-blue-600 hover:text-blue-500"
          >
            Forgot password?
          </Link>
        </div>
        
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
      
      <div className="mt-6">
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
          className="mt-4 w-full flex items-center justify-center gap-2 bg-white text-gray-700 py-3 px-4 rounded-md border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
        >
          <Mail className="h-5 w-5" />
          Sign in with Magic Link
        </Link>
        
        <div className="mt-3 text-center text-sm text-gray-600">
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