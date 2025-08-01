import { useEffect, useState } from 'react'
import useImageStore from '../stores/imageStore'
import useAuthStore from '../stores/authStore'
import { imagesAPI } from '../api/images'
import ImageCard from '../components/ImageCard'

function PublicGallery() {
  const { publicImages, setPublicImages, isLoadingGallery, setIsLoadingGallery } = useImageStore()
  const { hasActiveSubscription } = useAuthStore()
  const [cursor, setCursor] = useState(null)
  const [hasMore, setHasMore] = useState(true)
  
  useEffect(() => {
    loadImages()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  
  const loadImages = async (loadMore = false) => {
    if (!loadMore) {
      setIsLoadingGallery(true)
    }
    
    try {
      const response = await imagesAPI.getPublicGallery(loadMore ? cursor : null)
      setPublicImages(response.images, loadMore)
      setCursor(response.next_cursor)
      setHasMore(!!response.next_cursor)
    } catch (error) {
      console.error('Failed to load public gallery:', error)
    } finally {
      setIsLoadingGallery(false)
    }
  }
  
  const handleLoadMore = () => {
    if (hasMore && !isLoadingGallery) {
      loadImages(true)
    }
  }
  
  if (isLoadingGallery && publicImages.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading gallery...</div>
      </div>
    )
  }
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Public Gallery</h1>
        <p className="text-gray-600">
          Browse reference images shared by the community.
          {!hasActiveSubscription() && ' Subscribe to access all features.'}
        </p>
      </div>
      
      {publicImages.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No images in the public gallery yet.
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {publicImages.map((image) => (
              <ImageCard key={image.id} image={image} />
            ))}
          </div>
          
          {hasMore && (
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

export default PublicGallery