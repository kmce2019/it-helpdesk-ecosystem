import axios from "axios"

/*
|--------------------------------------------------------------------------
| Base API Instance
|--------------------------------------------------------------------------
*/

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
})

/*
|--------------------------------------------------------------------------
| Auth Token Handling
|--------------------------------------------------------------------------
*/

// Attach token automatically if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Optional: auto-logout on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)

/*
|--------------------------------------------------------------------------
| Auth Service
|--------------------------------------------------------------------------
*/

export const authService = {
  login: (data) =>
    api.post(
      "/auth/token",
      new URLSearchParams(data),
      {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      }
    ),

  me: () => api.get("/auth/me"),

  register: (data) => api.post("/auth/register", data),

  registrationEnabled: () => api.get("/auth/registration-enabled"),
}

/*
|--------------------------------------------------------------------------
| Tickets Service
|--------------------------------------------------------------------------
*/

export const ticketsService = {
  getAll: () => api.get("/tickets"),
  getById: (id) => api.get(`/tickets/${id}`),
  create: (data) => api.post("/tickets", data),
  update: (id, data) => api.put(`/tickets/${id}`, data),
  delete: (id) => api.delete(`/tickets/${id}`),
}

/*
|--------------------------------------------------------------------------
| Assets Service
|--------------------------------------------------------------------------
*/

export const assetsService = {
  getAll: () => api.get("/assets"),
  getById: (id) => api.get(`/assets/${id}`),
  create: (data) => api.post("/assets", data),
  update: (id, data) => api.put(`/assets/${id}`, data),
  delete: (id) => api.delete(`/assets/${id}`),
}

/*
|--------------------------------------------------------------------------
| Reports Service
|--------------------------------------------------------------------------
*/

export const reportsService = {
  getSummary: () => api.get("/reports/summary"),
  getSlaReport: () => api.get("/reports/sla"),
}

/*
|--------------------------------------------------------------------------
| Settings Service
|--------------------------------------------------------------------------
*/

export const settingsService = {
  getSettings: () => api.get("/settings"),
  updateSettings: (data) => api.put("/settings", data),
}

/*
|--------------------------------------------------------------------------
| Export API Instance (optional)
|--------------------------------------------------------------------------
*/

export default api
