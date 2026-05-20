import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API methods
export const chatAPI = {
  sendMessage: (data) => api.post('/api/v1/chat/message', data),
  getSession: (sessionId) => api.get(`/api/v1/chat/sessions/${sessionId}`),
  listSessions: (limit = 20) => api.get('/api/v1/chat/sessions', { params: { limit } }),
  deleteSession: (sessionId) => api.delete(`/api/v1/chat/sessions/${sessionId}`),
}

export const stockAPI = {
  searchStocks: (query, limit = 10) =>
    api.get('/api/v1/stocks/search', { params: { query, limit } }),
  getStockPrice: (symbol) => api.get(`/api/v1/stocks/${symbol}/price`),
  getHistoricalData: (symbol, period = '1M', interval = '1D') =>
    api.get(`/api/v1/stocks/${symbol}/historical`, { params: { period, interval } }),
  getFundamentals: (symbol) => api.get(`/api/v1/stocks/${symbol}/fundamentals`),
  getTrending: (limit = 10) => api.get('/api/v1/stocks/trending', { params: { limit } }),
}

export const analysisAPI = {
  getComprehensiveAnalysis: (data) =>
    api.post('/api/v1/analysis/comprehensive', data),
  getQuickAnalysis: (symbol) => api.get(`/api/v1/analysis/${symbol}/quick`),
}

export const healthAPI = {
  check: () => api.get('/health'),
  detailedCheck: () => api.get('/health/detailed'),
}

export default api
