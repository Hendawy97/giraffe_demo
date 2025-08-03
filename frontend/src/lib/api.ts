/**
 * API client for backend communication
 */

import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth
api.interceptors.request.use((config) => {
  // Add auth token if available (client-side only)
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Demo API endpoints
export const demoApi = {
  getProjects: () => api.get('/demo/projects'),
  getProject: (id: string) => api.get(`/demo/projects/${id}`),
  getProjectLayers: (id: string) => api.get(`/demo/projects/${id}/layers`),
  getViewerConfig: () => api.get('/demo/viewer-config'),
}

// Health check
export const healthCheck = () => api.get('/health', { baseURL: API_BASE_URL })