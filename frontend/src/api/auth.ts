import api from './config'
import { User } from '../types/types'

export const authAPI = {
  // Get current user profile
  getProfile: async (): Promise<User> => {
    const response = await api.get<User>('/me')
    return response.data
  },
  
  // Update username
  updateUsername: async (username: string): Promise<User> => {
    const response = await api.patch<User>('/me/username', { username })
    return response.data
  },
  
  // Logout (if backend has logout endpoint)
  logout: async (): Promise<void> => {
    try {
      await api.post('/logout')
    } catch {
      // Logout endpoint might not exist, continue with local logout
    }
    localStorage.removeItem('authToken')
  }
}