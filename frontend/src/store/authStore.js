import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      initialize: () => {
        const token = localStorage.getItem('auth_token')
        const user = localStorage.getItem('user_data')
        
        if (token && user) {
          set({
            token,
            user: JSON.parse(user),
            isAuthenticated: true,
          })
        }
      },

      login: async (email, password) => {
        set({ isLoading: true })
        try {
          // Implement Cognito authentication here
          // For now, mock implementation
          const mockUser = {
            id: '123',
            email,
            name: 'Demo User',
          }
          const mockToken = 'mock-jwt-token'

          localStorage.setItem('auth_token', mockToken)
          localStorage.setItem('user_data', JSON.stringify(mockUser))

          set({
            user: mockUser,
            token: mockToken,
            isAuthenticated: true,
            isLoading: false,
          })

          return { success: true }
        } catch (error) {
          set({ isLoading: false })
          return { success: false, error: error.message }
        }
      },

      logout: () => {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user_data')
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      updateUser: (userData) => {
        set({ user: { ...get().user, ...userData } })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

export { useAuthStore }
