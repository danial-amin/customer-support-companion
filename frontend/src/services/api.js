import axios from 'axios'

// API Base URL configuration:
// - If VITE_API_URL is set (Railway/production), use it
// - If localhost, use http://localhost:8000 (local dev)
// - Otherwise, use empty string for relative URLs (Docker Compose with nginx proxy)
// 
// IMPORTANT: On Railway, you MUST set VITE_API_URL to your backend service URL
// Example: VITE_API_URL=https://your-backend-production.up.railway.app
// 
// Note: Vite environment variables are embedded at BUILD TIME, not runtime.
// If you change VITE_API_URL in Railway, you must rebuild the frontend service.

// Get the API URL from environment (set at build time)
const envApiUrl = import.meta.env.VITE_API_URL

// Determine API base URL
let API_BASE_URL
if (envApiUrl && envApiUrl.trim() !== '') {
  // Use the environment variable if set and not empty
  API_BASE_URL = envApiUrl.trim()
} else if (window.location.hostname === 'localhost') {
  // Local development
  API_BASE_URL = 'http://localhost:8000'
} else {
  // Docker Compose or Railway without VITE_API_URL (will use relative URLs)
  API_BASE_URL = ''
}

// Debug logging (always log in development, optional in production)
if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
  console.log('🔧 API Configuration:', {
    'VITE_API_URL (env)': envApiUrl,
    'API_BASE_URL (resolved)': API_BASE_URL,
    'hostname': window.location.hostname,
    'origin': window.location.origin
  })
}
const API_KEY = import.meta.env.VITE_API_KEY || ''

// Create axios instance with conditional headers
const headers = {
  'Content-Type': 'application/json'
}

// Only add API key header if it's provided
if (API_KEY) {
  headers['X-API-Key'] = API_KEY
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: headers
})

export const checkHealth = async () => {
  const response = await apiClient.get('/api/v1/health')
  return response.data
}

export const queryAPI = async (query, agentType = 'auto') => {
  const response = await apiClient.post('/api/v1/query', {
    query,
    agent_type: agentType
  })
  return response.data
}

export const ragQuery = async (query) => {
  const response = await apiClient.post('/api/v1/rag', { query })
  return response.data
}

export const sqlQuery = async (query) => {
  const response = await apiClient.post('/api/v1/sql', { query })
  return response.data
}

export const analyzeQuery = async (query, data = null) => {
  const response = await apiClient.post('/api/v1/analyze', { query, data })
  return response.data
}

export const getSchema = async () => {
  const response = await apiClient.get('/api/v1/schema')
  return response.data
}

export const uploadDocument = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  // Create headers for file upload - DO NOT set Content-Type, let browser set it with boundary
  const uploadHeaders = {}
  if (API_KEY) {
    uploadHeaders['X-API-Key'] = API_KEY
  }
  
  // Use a fresh axios instance without default JSON headers for file uploads
  const uploadClient = axios.create({
    baseURL: API_BASE_URL,
    headers: uploadHeaders
    // Note: We intentionally don't set Content-Type - browser will set it with boundary
  })
  
  const response = await uploadClient.post('/api/v1/rag/upload', formData)
  return response.data
}

export const connectSharePoint = async (config) => {
  const response = await apiClient.post('/api/v1/rag/sharepoint', config)
  return response.data
}

