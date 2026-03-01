import { create } from 'zustand'
import { authService } from '../services/api'

export const useAuthStore = create((set) => ({
  user: localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null,
  token: localStorage.getItem('access_token') || null,
  isLoading: false,
  error: null,

  login: async (username, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authService.login(username, password)
      const { access_token, user } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('user', JSON.stringify(user))
      set({ user, token: access_token, isLoading: false })
      return true
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Login failed', isLoading: false })
      return false
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    set({ user: null, token: null })
  },

  checkAuth: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      set({ user: null, token: null })
      return false
    }
    try {
      const response = await authService.getMe()
      set({ user: response.data, token })
      return true
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      set({ user: null, token: null })
      return false
    }
  },
}))
