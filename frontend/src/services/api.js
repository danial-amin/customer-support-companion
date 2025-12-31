import axios from 'axios'

// Use relative URL to work through nginx proxy in Docker, or absolute URL for local dev
// In Docker, nginx proxies /api to backend:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '')
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
  
  // Create a new axios instance for file uploads (without Content-Type header)
  // Axios will automatically set the correct Content-Type with boundary
  const uploadHeaders = {}
  if (API_KEY) {
    uploadHeaders['X-API-Key'] = API_KEY
  }
  
  const response = await apiClient.post('/api/v1/rag/upload', formData, {
    headers: uploadHeaders
  })
  return response.data
}

export const connectSharePoint = async (config) => {
  const response = await apiClient.post('/api/v1/rag/sharepoint', config)
  return response.data
}

