import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
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
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return isAuthenticated ? children : <Navigate to="/login" state={{ from: location }} replace />
}

function App() {
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
