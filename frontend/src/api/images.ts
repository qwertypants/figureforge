import api from './config'
import { 
  GenerationParameters, 
  GenerationJob, 
  Image, 
  ToggleFavoriteResponse, 
  ReportImageResponse, 
  DeleteImageResponse,
  ReportForm
} from '../types/types'

interface ImagesResponse {
  images: Image[]
  next_cursor?: string
}

export const imagesAPI = {
  // Generate new images
  generate: async (params: GenerationParameters): Promise<GenerationJob> => {
    const response = await api.post<GenerationJob>('/generate', params)
    return response.data
  },
  
  // Get job status
  getJobStatus: async (jobId: string): Promise<GenerationJob> => {
    const response = await api.get<GenerationJob>(`/jobs/${jobId}`)
    return response.data
  },
  
  // Get public gallery
  getPublicGallery: async (cursor: string | null = null): Promise<ImagesResponse> => {
    const params = cursor ? { cursor } : {}
    const response = await api.get<ImagesResponse>('/images/public', { params })
    return response.data
  },
  
  // Get user's images
  getUserImages: async (cursor: string | null = null): Promise<ImagesResponse> => {
    const params = cursor ? { cursor } : {}
    const response = await api.get<ImagesResponse>('/images', { params })
    return response.data
  },
  
  // Get single image
  getImage: async (imageId: string): Promise<Image> => {
    const response = await api.get<Image>(`/images/${imageId}`)
    return response.data
  },
  
  // Toggle favorite
  toggleFavorite: async (imageId: string): Promise<ToggleFavoriteResponse> => {
    const response = await api.post<ToggleFavoriteResponse>(`/images/${imageId}/favorite`)
    return response.data
  },
  
  // Get favorites
  getFavorites: async (cursor: string | null = null): Promise<ImagesResponse> => {
    const params = cursor ? { cursor } : {}
    const response = await api.get<ImagesResponse>('/images/favorites', { params })
    return response.data
  },
  
  // Report image
  reportImage: async (imageId: string, reason: ReportForm['reason'], details: string): Promise<ReportImageResponse> => {
    const response = await api.post<ReportImageResponse>(`/images/${imageId}/report`, {
      reason,
      details
    })
    return response.data
  },
  
  // Delete image (if user owns it)
  deleteImage: async (imageId: string): Promise<DeleteImageResponse> => {
    const response = await api.delete<DeleteImageResponse>(`/images/${imageId}`)
    return response.data
  }
}