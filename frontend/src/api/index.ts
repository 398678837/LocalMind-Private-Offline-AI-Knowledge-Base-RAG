
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

function convertKB(data) {
  if (!data) return data
  return {
    id: data.id,
    name: data.name,
    description: data.description,
    fileCount: data.file_count,
    createdAt: data.created_at,
    updatedAt: data.updated_at
  }
}

function convertDoc(data) {
  if (!data) return data
  return {
    id: data.id,
    name: data.name,
    originalName: data.original_name,
    fileType: data.file_type,
    fileSize: data.file_size,
    knowledgeBaseId: data.knowledge_base_id,
    status: data.status,
    statusMessage: data.status_message,
    chunkCount: data.chunk_count,
    createdAt: data.created_at,
    updatedAt: data.updated_at
  }
}

export const knowledgeBaseApi = {
  getAll: async () => {
    const response = await api.get('/knowledge-bases')
    const convertedData = response.data.data?.map(convertKB) || []
    return { ...response.data, data: convertedData }
  },

  getById: async (kbId) => {
    const response = await api.get(`/knowledge-bases/${kbId}`)
    return { ...response.data, data: convertKB(response.data.data) }
  },

  create: async (data) => {
    const response = await api.post('/knowledge-bases', data)
    return { ...response.data, data: convertKB(response.data.data) }
  },

  update: async (kbId, data) => {
    const response = await api.put(`/knowledge-bases/${kbId}`, data)
    return { ...response.data, data: convertKB(response.data.data) }
  },

  delete: async (kbId) => {
    const response = await api.delete(`/knowledge-bases/${kbId}`)
    return response.data
  }
}

export const documentApi = {
  upload: async (file, knowledgeBaseId) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('knowledge_base_id', knowledgeBaseId)
    
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return { ...response.data, data: convertDoc(response.data.data) }
  },

  getByKnowledgeBase: async (kbId) => {
    const response = await api.get(`/knowledge-bases/${kbId}/files`)
    const convertedData = response.data.data?.map(convertDoc) || []
    return { ...response.data, data: convertedData }
  },

  getById: async (docId) => {
    const response = await api.get(`/files/${docId}`)
    return { ...response.data, data: convertDoc(response.data.data) }
  },

  delete: async (docId) => {
    const response = await api.delete(`/files/${docId}`)
    return response.data
  }
}

function convertSession(data) {
  if (!data) return data
  return {
    id: data.id,
    knowledgeBaseId: data.knowledge_base_id,
    title: data.title,
    createdAt: data.created_at,
    updatedAt: data.updated_at
  }
}

function convertMessage(data) {
  if (!data) return data
  return {
    id: data.id,
    role: data.role,
    content: data.content,
    createdAt: data.created_at
  }
}

export const chatApi = {
  createSession: async (data) => {
    const response = await api.post('/chat/sessions', {
      knowledge_base_id: data.knowledgeBaseId,
      title: data.title
    })
    return { ...response.data, data: convertSession(response.data.data) }
  },

  listSessions: async (knowledgeBaseId) => {
    const params = knowledgeBaseId ? { knowledge_base_id: knowledgeBaseId } : {}
    const response = await api.get('/chat/sessions', { params })
    const convertedData = response.data.data?.map(convertSession) || []
    return { ...response.data, data: convertedData }
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/chat/sessions/${sessionId}`)
    return { ...response.data, data: convertSession(response.data.data) }
  },

  updateSessionTitle: async (sessionId, title) => {
    const response = await api.put(`/chat/sessions/${sessionId}/title?title=${encodeURIComponent(title)}`)
    return { ...response.data, data: convertSession(response.data.data) }
  },

  deleteSession: async (sessionId) => {
    const response = await api.delete(`/chat/sessions/${sessionId}`)
    return response.data
  },

  getSessionMessages: async (sessionId) => {
    const response = await api.get(`/chat/sessions/${sessionId}/messages`)
    const convertedData = response.data.data?.map(convertMessage) || []
    return { ...response.data, data: convertedData }
  },

  sendMessage: async (data) => {
    const response = await api.post('/chat/send', {
      session_id: data.sessionId,
      knowledge_base_id: data.knowledgeBaseId,
      query: data.query,
      stream: data.stream || false
    })
    return { ...response.data, data: convertMessage(response.data.data) }
  },

  checkOllamaStatus: async () => {
    const response = await api.get('/chat/ollama/status')
    return response.data
  }
}

export const systemApi = {
  getStatus: async () => {
    const response = await api.get('/status')
    return response.data
  }
}

export default api
