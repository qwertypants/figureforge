import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuth } from 'react-oidc-context'
import useAuthStore from './stores/authStore'
import { authAPI } from './api/auth'
import type { ProtectedRouteProps } from './types/types'

// Layout
import Layout from './components/Layout'

// Pages
import Home from './pages/Home'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Generate from './pages/Generate'
import PublicGallery from './pages/PublicGallery'
import MyImages from './pages/MyImages'
import Account from './pages/Account'
import Pricing from './pages/Pricing'
import AuthCallback from './pages/AuthCallback'
import MagicLinkLogin from './pages/MagicLinkLogin'
import MagicLinkCallback from './pages/MagicLinkCallback'

// Protected Route component
function ProtectedRoute({ children }: ProtectedRouteProps) {
  const auth = useAuth()
  const { isAuthenticated } = useAuthStore()
  const location = useLocation()

  // Use OIDC auth state if available, otherwise fall back to store
  const isUserAuthenticated = auth.isAuthenticated || isAuthenticated

  if (auth.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return isUserAuthenticated ? children : <Navigate to="/login" state={{ from: location }} replace />
}

function App() {
  const auth = useAuth()
  const { setUser, setLoading } = useAuthStore()

  // Sync OIDC auth state with app store
  useEffect(() => {
    const syncAuth = async () => {
      setLoading(auth.isLoading)

      if (auth.isAuthenticated && auth.user) {
        try {
          // Set the auth token for API calls
          localStorage.setItem('authToken', auth.user.id_token || '')

          // Get user profile from backend
          const userProfile = await authAPI.getProfile()
          setUser(userProfile)
        } catch (error) {
          console.error('Failed to get user profile:', error)
        }
      } else if (!auth.isLoading && !auth.isAuthenticated) {
        // Clear user data when not authenticated
        setUser(null)
        localStorage.removeItem('authToken')
      }
    }

    syncAuth()
  }, [auth.isAuthenticated, auth.isLoading, auth.user, setUser, setLoading])

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="login" element={<Login />} />
          <Route path="login/magic-link" element={<MagicLinkLogin />} />
          <Route path="signup" element={<SignUp />} />
          <Route path="pricing" element={<Pricing />} />
          <Route path="gallery" element={<PublicGallery />} />
          <Route path="auth/callback" element={<AuthCallback />} />
          <Route path="auth/magic-link" element={<MagicLinkCallback />} />

          {/* Protected routes */}
          <Route
            path="generate"
            element={
              <ProtectedRoute>
                <Generate />
              </ProtectedRoute>
            }
          />
          <Route
            path="my-images"
            element={
              <ProtectedRoute>
                <MyImages />
              </ProtectedRoute>
            }
          />
          <Route
            path="account"
            element={
              <ProtectedRoute>
                <Account />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
