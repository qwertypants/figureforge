import api from './config'

export const authAPI = {
  // Get current user profile
  getProfile: async () => {
    const response = await api.get('/me')
    return response.data
  },
  
  // Update username
  updateUsername: async (username) => {
    const response = await api.patch('/me/username', { username })
    return response.data
  },
  
  // Logout (if backend has logout endpoint)
  logout: async () => {
    try {
      await api.post('/logout')
    } catch {
      // Logout endpoint might not exist, continue with local logout
    }
    localStorage.removeItem('authToken')
  }
}