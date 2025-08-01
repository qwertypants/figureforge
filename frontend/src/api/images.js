import api from './config'

export const imagesAPI = {
  // Generate new images
  generate: async (params) => {
    const response = await api.post('/generate', params)
    return response.data
  },
  
  // Get job status
  getJobStatus: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}`)
    return response.data
  },
  
  // Get public gallery
  getPublicGallery: async (cursor = null) => {
    const params = cursor ? { cursor } : {}
    const response = await api.get('/images/public', { params })
    return response.data
  },
  
  // Get user's images
  getUserImages: async (cursor = null) => {
    const params = cursor ? { cursor } : {}
    const response = await api.get('/images', { params })
    return response.data
  },
  
  // Get single image
  getImage: async (imageId) => {
    const response = await api.get(`/images/${imageId}`)
    return response.data
  },
  
  // Toggle favorite
  toggleFavorite: async (imageId) => {
    const response = await api.post(`/images/${imageId}/favorite`)
    return response.data
  },
  
  // Get favorites
  getFavorites: async (cursor = null) => {
    const params = cursor ? { cursor } : {}
    const response = await api.get('/images/favorites', { params })
    return response.data
  },
  
  // Report image
  reportImage: async (imageId, reason, details) => {
    const response = await api.post(`/images/${imageId}/report`, {
      reason,
      details
    })
    return response.data
  },
  
  // Delete image (if user owns it)
  deleteImage: async (imageId) => {
    const response = await api.delete(`/images/${imageId}`)
    return response.data
  }
}