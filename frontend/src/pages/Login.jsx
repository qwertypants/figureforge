import { useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from 'react-oidc-context'
import useAuthStore from '../stores/authStore'

function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const auth = useAuth()
  const { error } = useAuthStore()
  
  // Redirect if already authenticated
  useEffect(() => {
    if (auth.isAuthenticated) {
      const from = location.state?.from?.pathname || '/generate'
      navigate(from, { replace: true })
    }
  }, [auth.isAuthenticated, navigate, location])
  
  const handleLogin = () => {
    // Store the intended destination
    const from = location.state?.from?.pathname || '/generate'
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
        
        <div className="text-center text-sm text-gray-600">
          Sign in using your email and password through AWS Cognito
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