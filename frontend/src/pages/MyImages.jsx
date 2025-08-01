import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import useImageStore from '../stores/imageStore'
import { imagesAPI } from '../api/images'
import ImageCard from '../components/ImageCard'

function MyImages() {
  const { userImages, setUserImages, favorites, setFavorites, isLoadingGallery, setIsLoadingGallery } = useImageStore()
  const [cursor, setCursor] = useState(null)
  const [hasMore, setHasMore] = useState(true)
  const [view, setView] = useState('all') // 'all' or 'favorites'
  
  useEffect(() => {
    if (view === 'all') {
      loadUserImages()
    } else {
      loadFavorites()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view])
  
  const loadUserImages = async (loadMore = false) => {
    if (!loadMore) {
      setIsLoadingGallery(true)
    }
    
    try {
      const response = await imagesAPI.getUserImages(loadMore ? cursor : null)
      setUserImages(response.images, loadMore)
      setCursor(response.next_cursor)
      setHasMore(!!response.next_cursor)
    } catch (error) {
      console.error('Failed to load user images:', error)
    } finally {
      setIsLoadingGallery(false)
    }
  }
  
  const loadFavorites = async () => {
    setIsLoadingGallery(true)
    
    try {
      const response = await imagesAPI.getFavorites()
      setFavorites(response.images)
    } catch (error) {
      console.error('Failed to load favorites:', error)
    } finally {
      setIsLoadingGallery(false)
    }
  }
  
  const handleLoadMore = () => {
    if (hasMore && !isLoadingGallery && view === 'all') {
      loadUserImages(true)
    }
  }
  
  const displayImages = view === 'all' ? userImages : favorites
  
  if (isLoadingGallery && displayImages.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading your images...</div>
      </div>
    )
  }
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">My Images</h1>
        <p className="text-gray-600">
          Your personal library of generated reference images.
        </p>
      </div>
      
      <div className="mb-6 flex gap-4">
        <button
          onClick={() => setView('all')}
          className={`px-4 py-2 rounded-md ${
            view === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          All Images
        </button>
        <button
          onClick={() => setView('favorites')}
          className={`px-4 py-2 rounded-md ${
            view === 'favorites'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Favorites
        </button>
      </div>
      
      {displayImages.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">
            {view === 'all' 
              ? "You haven't generated any images yet." 
              : "You haven't favorited any images yet."}
          </p>
          {view === 'all' && (
            <Link
              to="/generate"
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 inline-block"
            >
              Generate Your First Image
            </Link>
          )}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {displayImages.map((image) => (
              <ImageCard key={image.id} image={image} showActions />
            ))}
          </div>
          
          {hasMore && view === 'all' && (
            <div className="mt-8 text-center">
              <button
                onClick={handleLoadMore}
                disabled={isLoadingGallery}
                className="bg-gray-200 text-gray-900 px-6 py-2 rounded-md hover:bg-gray-300 disabled:opacity-50"
              >
                {isLoadingGallery ? 'Loading...' : 'Load More'}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default MyImages