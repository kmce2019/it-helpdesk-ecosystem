import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authService = {
  login: (data) => api.post('/auth/token', data),
  me: () => api.get('/auth/me'),
  register: (data) => api.post('/auth/register', data),
  registrationEnabled: () => api.get('/auth/registration-enabled'),
}

export const ticketsService = {
  list: (params) => api.get('/tickets', { params }),
  get: (id) => api.get(`/tickets/${id}`),
  create: (data) => api.post('/tickets', data),
  update: (id, data) => api.put(`/tickets/${id}`, data),
  delete: (id) => api.delete(`/tickets/${id}`),
  addComment: (id, data) => api.post(`/tickets/${id}/comments`, data),
}

export const assetsService = {
  list: (params) => api.get('/assets', { params }),
  get: (id) => api.get(`/assets/${id}`),
  getCves: (id, params) => api.get(`/assets/${id}/cves`, { params }),
  acknowledgeCve: (assetId, cveId) => api.put(`/assets/${assetId}/cves/${cveId}/acknowledge`),
  update: (id, data) => api.put(`/assets/${id}`, data),
  delete: (id) => api.delete(`/assets/${id}`),
}

export const reportingService = {
  getDashboard: () => api.get('/reports/dashboard'),
  getTicketsByStatus: () => api.get('/reports/tickets/by-status'),
  getTicketsByPriority: () => api.get('/reports/tickets/by-priority'),
  getTicketsByCategory: () => api.get('/reports/tickets/by-category'),
  getResolutionTime: (days) => api.get('/reports/tickets/resolution-time', { params: { days } }),
  getCvesBySeverity: () => api.get('/reports/cves/by-severity'),
  getUnacknowledgedCves: (severity) => api.get('/reports/cves/unacknowledged', { params: { severity } }),
  getAssetsByType: () => api.get('/reports/assets/by-type'),
  getAssetsByDepartment: () => api.get('/reports/assets/by-department'),
  getSlaCompliance: (days) => api.get('/reports/sla/compliance', { params: { days } }),
}

export const usersService = {
  list: () => api.get('/users'),
  get: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
}

export const slasService = {
  list: () => api.get('/slas'),
  get: (id) => api.get(`/slas/${id}`),
  create: (data) => api.post('/slas', data),
  update: (id, data) => api.put(`/slas/${id}`, data),
  delete: (id) => api.delete(`/slas/${id}`),
}

export const settingsService = {
  getAll: () => api.get('/settings'),
  get: (key) => api.get(`/settings/${key}`),
  update: (key, data) => api.put(`/settings/${key}`, data),
  testEmail: (data) => api.post('/settings/test/email', data),
  testGoogleChat: (data) => api.post('/settings/test/google-chat', data),
}

export default api
