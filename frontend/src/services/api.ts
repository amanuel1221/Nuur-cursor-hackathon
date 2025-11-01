import axios, { AxiosError, AxiosRequestConfig } from 'axios'
import { useAuthStore } from '../store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const { refreshToken } = useAuthStore.getState()
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token } = response.data
        const { user } = useAuthStore.getState()
        
        if (user) {
          useAuthStore.getState().setAuth(user, access_token, refresh_token)
        }

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }

        return api(originalRequest)
      } catch (refreshError) {
        useAuthStore.getState().clearAuth()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api

// API response wrapper
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: {
    code: number
    message: string
    details?: any
  }
}

// Auth API
export const authApi = {
  register: (data: any) => api.post<ApiResponse>('/auth/register', data),
  login: (data: any) => api.post<ApiResponse>('/auth/login', data),
  logout: () => api.post<ApiResponse>('/auth/logout'),
}

// User API
export const userApi = {
  getProfile: () => api.get<ApiResponse>('/users/me'),
  updateProfile: (data: any) => api.put<ApiResponse>('/users/me', data),
  getContacts: () => api.get<ApiResponse>('/users/contacts'),
  addContact: (data: any) => api.post<ApiResponse>('/users/contacts', data),
  updateContact: (id: string, data: any) => api.put<ApiResponse>(`/users/contacts/${id}`, data),
  deleteContact: (id: string) => api.delete<ApiResponse>(`/users/contacts/${id}`),
}

// Anti-Theft API
export const antiTheftApi = {
  setup: (data: any) => api.post<ApiResponse>('/anti-theft/setup', data),
  getConfig: () => api.get<ApiResponse>('/anti-theft/config'),
  trigger: (data: any) => api.post<ApiResponse>('/anti-theft/trigger', data),
  getStatus: () => api.get<ApiResponse>('/anti-theft/status'),
  addLocation: (eventId: string, data: any) => 
    api.post<ApiResponse>(`/anti-theft/events/${eventId}/location`, data),
  deactivate: (eventId: string) => 
    api.post<ApiResponse>(`/anti-theft/events/${eventId}/deactivate`),
  getEvents: (limit?: number) => 
    api.get<ApiResponse>('/anti-theft/events', { params: { limit } }),
}

// Path Tracking API
export const pathApi = {
  start: (data: any) => api.post<ApiResponse>('/paths/start', data),
  stop: (pathId: string) => api.post<ApiResponse>(`/paths/${pathId}/stop`),
  addPoints: (pathId: string, points: any[]) => 
    api.post<ApiResponse>(`/paths/${pathId}/points`, points),
  getList: (limit?: number, skip?: number) => 
    api.get<ApiResponse>('/paths', { params: { limit, skip } }),
  getDetail: (pathId: string) => api.get<ApiResponse>(`/paths/${pathId}`),
  update: (pathId: string, data: any) => api.put<ApiResponse>(`/paths/${pathId}`, data),
  delete: (pathId: string) => api.delete<ApiResponse>(`/paths/${pathId}`),
  share: (pathId: string, data: any) => 
    api.post<ApiResponse>(`/paths/${pathId}/share`, data),
  getShared: (token: string) => api.get<ApiResponse>(`/paths/shared/${token}`),
}

// Emergency API
export const emergencyApi = {
  report: (data: any) => api.post<ApiResponse>('/emergency/report', data),
  getReports: (limit?: number, skip?: number) => 
    api.get<ApiResponse>('/emergency/reports', { params: { limit, skip } }),
  getDetail: (reportId: string) => api.get<ApiResponse>(`/emergency/reports/${reportId}`),
  updateStatus: (reportId: string, data: any) => 
    api.put<ApiResponse>(`/emergency/reports/${reportId}/status`, data),
  uploadMedia: (reportId: string, file: File, mediaType: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('media_type', mediaType)
    return api.post<ApiResponse>(`/emergency/reports/${reportId}/media`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getNearby: (lat: number, lon: number, radius?: number) => 
    api.get<ApiResponse>('/emergency/nearby', {
      params: { latitude: lat, longitude: lon, radius_km: radius },
    }),
}

