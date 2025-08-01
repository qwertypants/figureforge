import { Link } from 'react-router-dom'
import useAuthStore from '../stores/authStore'

function Home() {
  const { isAuthenticated } = useAuthStore()
  
  return (
    <div className="text-center">
      <h1 className="text-5xl font-bold text-gray-900 mb-4">
        AI-Powered Figure Drawing References
      </h1>
      <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
        Generate customizable, SFW human figure references for your art practice. 
        Perfect for artists looking to improve their figure drawing skills.
      </p>
      
      <div className="flex justify-center gap-4">
        {isAuthenticated ? (
          <Link
            to="/generate"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg text-lg font-medium hover:bg-blue-700"
          >
            Start Generating
          </Link>
        ) : (
          <>
            <Link
              to="/signup"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg text-lg font-medium hover:bg-blue-700"
            >
              Get Started
            </Link>
            <Link
              to="/pricing"
              className="bg-gray-200 text-gray-900 px-6 py-3 rounded-lg text-lg font-medium hover:bg-gray-300"
            >
              View Pricing
            </Link>
          </>
        )}
      </div>
      
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-2">Customizable Poses</h3>
          <p className="text-gray-600">
            Choose from various poses, body types, and camera angles to match your study needs.
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-2">Professional Lighting</h3>
          <p className="text-gray-600">
            Multiple lighting options to help you understand form, shadow, and anatomy.
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-2">Build Your Library</h3>
          <p className="text-gray-600">
            Save your favorite references and organize them for easy access during practice.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Home