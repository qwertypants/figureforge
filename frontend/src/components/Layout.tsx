import { Link, Outlet } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import useAuthStore from '../stores/authStore'
import { LayoutProps } from '../types/types'

function Layout({}: LayoutProps) {
  const { isAuthenticated, signOut } = useAuth()
  const { user } = useAuthStore()
  
  const handleLogout = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Logout failed:', error)
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
                <Link
                  to="/gallery"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 border-b-2 border-transparent hover:border-gray-300"
                >
                  Gallery
                </Link>
                <Link
                  to="/pricing"
                  className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 border-b-2 border-transparent hover:border-gray-300"
                >
                  Pricing
                </Link>
                {isAuthenticated && (
                  <>
                    <Link
                      to="/generate"
                      className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 border-b-2 border-transparent hover:border-gray-300"
                    >
                      Generate
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
              {isAuthenticated ? (
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