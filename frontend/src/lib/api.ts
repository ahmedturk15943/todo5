/**
 * API client for communicating with the backend.
 */

import axios, { AxiosInstance, AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Request interceptor to add JWT token
apiClient.interceptors.request.use(
  config => {
    // Get token from localStorage or cookie
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to signin
      localStorage.removeItem('auth_token')
      if (typeof window !== 'undefined') {
        window.location.href = '/signin'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient

// ==================== Recurring Tasks API ====================

export async function getRecurringPatterns() {
  const response = await apiClient.get('/api/recurring')
  return response.data
}

export async function createRecurringPattern(pattern: any) {
  const response = await apiClient.post('/api/recurring', pattern)
  return response.data
}

export async function getRecurringPattern(patternId: number) {
  const response = await apiClient.get(`/api/recurring/${patternId}`)
  return response.data
}

export async function deactivateRecurringPattern(patternId: number) {
  await apiClient.delete(`/api/recurring/${patternId}`)
}

// ==================== Reminders API ====================

export async function createReminder(taskId: number, remindAt: string) {
  const response = await apiClient.post('/api/reminders', {
    task_id: taskId,
    remind_at: remindAt
  })
  return response.data
}

export async function listReminders(taskId?: number, status?: string) {
  const params = new URLSearchParams()
  if (taskId) params.append('task_id', taskId.toString())
  if (status) params.append('status', status)

  const response = await apiClient.get(`/api/reminders?${params}`)
  return response.data
}

export async function cancelReminder(reminderId: number) {
  await apiClient.delete(`/api/reminders/${reminderId}`)
}

// ==================== Tags API ====================

export async function getTags() {
  const response = await apiClient.get('/api/tags')
  return response.data
}

export async function createTag(tag: { name: string; color?: string }) {
  const response = await apiClient.post('/api/tags', tag)
  return response.data
}

export async function updateTag(tagId: number, tag: { name?: string; color?: string }) {
  const response = await apiClient.put(`/api/tags/${tagId}`, tag)
  return response.data
}

export async function deleteTag(tagId: number) {
  await apiClient.delete(`/api/tags/${tagId}`)
}

export async function addTagToTask(taskId: number, tagId: number) {
  await apiClient.post(`/api/tasks/${taskId}/tags/${tagId}`)
}

export async function removeTagFromTask(taskId: number, tagId: number) {
  await apiClient.delete(`/api/tasks/${taskId}/tags/${tagId}`)
}

// ==================== Activity API ====================

export async function getUserActivities(params?: {
  limit?: number;
  offset?: number;
  action?: string;
  entity_type?: string;
}) {
  const queryParams = new URLSearchParams()
  if (params?.limit) queryParams.append('limit', params.limit.toString())
  if (params?.offset) queryParams.append('offset', params.offset.toString())
  if (params?.action) queryParams.append('action', params.action)
  if (params?.entity_type) queryParams.append('entity_type', params.entity_type)

  const response = await apiClient.get(`/api/activity?${queryParams}`)
  return response.data
}

export async function getTaskActivities(taskId: number, params?: {
  limit?: number;
  offset?: number;
}) {
  const queryParams = new URLSearchParams()
  if (params?.limit) queryParams.append('limit', params.limit.toString())
  if (params?.offset) queryParams.append('offset', params.offset.toString())

  const response = await apiClient.get(`/api/activity/task/${taskId}?${queryParams}`)
  return response.data
}

export async function getRecentActivities(params?: {
  hours?: number;
  limit?: number;
}) {
  const queryParams = new URLSearchParams()
  if (params?.hours) queryParams.append('hours', params.hours.toString())
  if (params?.limit) queryParams.append('limit', params.limit.toString())

  const response = await apiClient.get(`/api/activity/recent?${queryParams}`)
  return response.data
}

// Helper function to set auth token
export const setAuthToken = (token: string) => {
  localStorage.setItem('auth_token', token)
}

// Helper function to clear auth token
export const clearAuthToken = () => {
  localStorage.removeItem('auth_token')
}

// Helper function to get auth token
export const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token')
}
