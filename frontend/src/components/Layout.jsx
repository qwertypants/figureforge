import { Link, Outlet } from 'react-router-dom'
import { useAuth } from 'react-oidc-context'
import useAuthStore from '../stores/authStore'

function Layout() {
  const auth = useAuth()
  const { user, isAuthenticated } = useAuthStore()
  
  // Use OIDC auth state if available
  const isUserAuthenticated = auth.isAuthenticated || isAuthenticated
  
  const handleLogout = () => {
    // Clear local auth state first
    auth.removeUser()
    useAuthStore.getState().logout()
    
    // Redirect to Cognito logout
    const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID
    const logoutUri = import.meta.env.VITE_LOGOUT_URI || window.location.origin
    const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN
    
    if (cognitoDomain && clientId) {
      window.location.href = `${cognitoDomain}/logout?client_id=${clientId}&logout_uri=${encodeURIComponent(logoutUri)}`
    }
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/" className="flex items-center">
                <h1 className="text-xl font-bold text-gray-900">FigureForge</h1>
              </Link>
              
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {isUserAuthenticated && (
                  <>
                    <Link
                      to="/generate"
                      className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 border-b-2 border-transparent hover:border-gray-300"
                    >
                      Generate
                    </Link>
                    <Link
                      to="/gallery"
                      className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 border-b-2 border-transparent hover:border-gray-300"
                    >
                      Public Gallery
                    </Link>
                    <Link
                      to="/my-images"
                      className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 border-b-2 border-transparent hover:border-gray-300"
                    >
                      My Images
                    </Link>
                  </>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {isUserAuthenticated ? (
                <>
                  <Link
                    to="/account"
                    className="text-sm font-medium text-gray-700 hover:text-gray-900"
                  >
                    {user?.username || user?.email}
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="text-sm font-medium text-gray-700 hover:text-gray-900"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="text-sm font-medium text-gray-700 hover:text-gray-900"
                  >
                    Login
                  </Link>
                  <Link
                    to="/signup"
                    className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout