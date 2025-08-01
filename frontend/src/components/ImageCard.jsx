import { useState } from 'react'
import useImageStore from '../stores/imageStore'
import useAuthStore from '../stores/authStore'
import { imagesAPI } from '../api/images'

function ImageCard({ image, showActions = false }) {
  const { isFavorited, addToFavorites, removeFromFavorites } = useImageStore()
  const { isAuthenticated } = useAuthStore()
  const [isReporting, setIsReporting] = useState(false)
  const [reportReason, setReportReason] = useState('')
  const [reportDetails, setReportDetails] = useState('')
  
  const handleToggleFavorite = async () => {
    try {
      await imagesAPI.toggleFavorite(image.id)
      if (isFavorited(image.id)) {
        removeFromFavorites(image.id)
      } else {
        addToFavorites(image.id)
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error)
    }
  }
  
  const handleReport = async (e) => {
    e.preventDefault()
    try {
      await imagesAPI.reportImage(image.id, reportReason, reportDetails)
      setIsReporting(false)
      setReportReason('')
      setReportDetails('')
      alert('Image reported successfully')
    } catch (error) {
      console.error('Failed to report image:', error)
      alert('Failed to report image')
    }
  }
  
  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this image?')) {
      try {
        await imagesAPI.deleteImage(image.id)
        // Refresh the gallery
        window.location.reload()
      } catch (error) {
        console.error('Failed to delete image:', error)
        alert('Failed to delete image')
      }
    }
  }
  
  return (
    <div className="relative group">
      <img
        src={image.thumbnail_url || image.url}
        alt="Figure reference"
        className="w-full h-auto rounded-lg shadow-md"
      />
      
      {/* Overlay actions */}
      {isAuthenticated && (
        <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleToggleFavorite}
            className="bg-white p-2 rounded-full shadow-lg hover:bg-gray-100"
            title={isFavorited(image.id) ? 'Remove from favorites' : 'Add to favorites'}
          >
            <svg
              className={`w-5 h-5 ${isFavorited(image.id) ? 'text-red-500' : 'text-gray-600'}`}
              fill={isFavorited(image.id) ? 'currentColor' : 'none'}
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
              />
            </svg>
          </button>
          
          {!showActions && (
            <button
              onClick={() => setIsReporting(true)}
              className="bg-white p-2 rounded-full shadow-lg hover:bg-gray-100"
              title="Report image"
            >
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </button>
          )}
          
          {showActions && (
            <button
              onClick={handleDelete}
              className="bg-white p-2 rounded-full shadow-lg hover:bg-gray-100"
              title="Delete image"
            >
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          )}
        </div>
      )}
      
      {/* Report modal */}
      {isReporting && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Report Image</h3>
            <form onSubmit={handleReport}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reason
                </label>
                <select
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select a reason</option>
                  <option value="inappropriate">Inappropriate content</option>
                  <option value="copyright">Copyright violation</option>
                  <option value="quality">Low quality</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Details (optional)
                </label>
                <textarea
                  value={reportDetails}
                  onChange={(e) => setReportDetails(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="flex-1 bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700"
                >
                  Report
                </button>
                <button
                  type="button"
                  onClick={() => setIsReporting(false)}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default ImageCard