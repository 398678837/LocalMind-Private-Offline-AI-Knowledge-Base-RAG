
export interface KnowledgeBase {
  id: string
  name: string
  description?: string
  fileCount: number
  createdAt: string
  updatedAt: string
}

export type FileStatus = 'uploaded' | 'processing' | 'processed' | 'error'
export type FileType = 'pdf' | 'docx' | 'txt' | 'md' | 'py' | 'java'

export interface Document {
  id: string
  name: string
  originalName: string
  fileType: FileType
  fileSize: number
  knowledgeBaseId: string
  status: FileStatus
  statusMessage?: string
  chunkCount: number
  createdAt: string
  updatedAt: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  cot?: CotStep[]
  relatedDocs?: Document[]
}

export interface CotStep {
  type: 'thought' | 'action' | 'observation'
  content: string
}

export interface SystemStatus {
  app_name: string
  version: string
  ollama_url: string
  ollama_model: string
  embedding_model: string
  file_encryption_enabled: boolean
  sensitive_detection_enabled: boolean
}

export interface ChatSession {
  id: string
  knowledgeBaseId: string
  title?: string
  createdAt: string
  updatedAt: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  createdAt: string
}
