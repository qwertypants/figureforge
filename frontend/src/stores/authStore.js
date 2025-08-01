import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      setUser: (user) => set({ 
        user, 
        isAuthenticated: !!user,
        error: null 
      }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      setError: (error) => set({ error }),
      
      logout: () => set({ 
        user: null, 
        isAuthenticated: false,
        error: null 
      }),
      
      clearError: () => set({ error: null }),
      
      hasActiveSubscription: () => {
        const { user } = get()
        return user?.subscription?.status === 'active'
      },
      
      getQuotaRemaining: () => {
        const { user } = get()
        if (!user?.subscription) return 0
        return user.subscription.quota_remaining || 0
      },
      
      isAdmin: () => {
        const { user } = get()
        return user?.role === 'admin'
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated 
      })
    }
  )
)

export default useAuthStore