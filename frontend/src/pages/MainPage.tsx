import { useState, useEffect, useRef } from 'react'
import type { KnowledgeBase, Document, ChatSession, ChatMessage } from '../types'
import { knowledgeBaseApi, documentApi, chatApi } from '../api'

const statusColors: Record<string, string> = {
  uploaded: 'bg-yellow-100 text-yellow-800',
  processing: 'bg-blue-100 text-blue-800',
  processed: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800'
}

const statusLabels: Record<string, string> = {
  uploaded: '已上传',
  processing: '处理中',
  processed: '已完成',
  error: '处理失败'
}

const fileTypeIcons: Record<string, string> = {
  pdf: '📄',
  docx: '📝',
  txt: '📃',
  md: '📑',
  py: '🐍',
  java: '☕'
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

export default function MainPage() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKB, setSelectedKB] = useState<string>('')
  const [kbLoading, setKbLoading] = useState(true)
  
  const [documents, setDocuments] = useState<Document[]>([])
  const [docsLoading, setDocsLoading] = useState(false)
  
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const [showNewKbModal, setShowNewKbModal] = useState(false)
  const [showEditKbModal, setShowEditKbModal] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showDeleteDocConfirm, setShowDeleteDocConfirm] = useState(false)
  const [showDeleteSessionConfirm, setShowDeleteSessionConfirm] = useState(false)
  
  const [kbFormData, setKbFormData] = useState({ name: '', description: '' })
  const [editingKbId, setEditingKbId] = useState('')
  const [deletingKbId, setDeletingKbId] = useState('')
  const [deletingDocId, setDeletingDocId] = useState('')
  const [deletingSessionId, setDeletingSessionId] = useState('')
  
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const [selectedSession, setSelectedSession] = useState<string>('')
  
  const [editingSessionId, setEditingSessionId] = useState<string>('')
  const [editingSessionTitle, setEditingSessionTitle] = useState('')
  const [pinnedSessions, setPinnedSessions] = useState<string[]>(() => {
    const saved = localStorage.getItem('pinnedSessions')
    return saved ? JSON.parse(saved) : []
  })
  
  useEffect(() => {
    localStorage.setItem('pinnedSessions', JSON.stringify(pinnedSessions))
  }, [pinnedSessions])
  
  const [sessionsLoading, setSessionsLoading] = useState(false)
  
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [messagesLoading, setMessagesLoading] = useState(false)
  
  const [messageInput, setMessageInput] = useState('')
  const [sendingMessage, setSendingMessage] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  useEffect(() => {
    if (selectedKB) {
      loadDocuments(selectedKB)
      loadChatSessions(selectedKB)
    } else {
      setDocuments([])
      setChatSessions([])
      setSelectedSession('')
      setMessages([])
    }
  }, [selectedKB])

  useEffect(() => {
    if (selectedSession) {
      loadMessages(selectedSession)
    } else {
      setMessages([])
    }
  }, [selectedSession])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadKnowledgeBases = async () => {
    try {
      setKbLoading(true)
      const response = await knowledgeBaseApi.getAll()
      if (response.success && response.data) {
        setKnowledgeBases(response.data)
        if (response.data.length > 0 && !selectedKB) {
          setSelectedKB(response.data[0].id)
        }
      }
    } catch (error) {
      console.error('加载知识库失败:', error)
    } finally {
      setKbLoading(false)
    }
  }

  const loadDocuments = async (kbId: string) => {
    try {
      setDocsLoading(true)
      const response = await documentApi.getByKnowledgeBase(kbId)
      if (response.success && response.data) {
        setDocuments(response.data)
      }
    } catch (error) {
      console.error('加载文件列表失败:', error)
    } finally {
      setDocsLoading(false)
    }
  }

  const handleCreateKnowledgeBase = async () => {
    if (!kbFormData.name.trim()) return

    try {
      const response = await knowledgeBaseApi.create({
        name: kbFormData.name,
        description: kbFormData.description
      })

      if (response.success) {
        resetForm()
        setShowNewKbModal(false)
        loadKnowledgeBases()
      }
    } catch (error) {
      console.error('创建知识库失败:', error)
    }
  }

  const handleOpenEditModal = (kb: KnowledgeBase, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingKbId(kb.id)
    setKbFormData({
      name: kb.name,
      description: kb.description || ''
    })
    setShowEditKbModal(true)
  }

  const handleUpdateKnowledgeBase = async () => {
    if (!kbFormData.name.trim()) return

    try {
      const response = await knowledgeBaseApi.update(editingKbId, {
        name: kbFormData.name,
        description: kbFormData.description
      })

      if (response.success) {
        resetForm()
        setShowEditKbModal(false)
        loadKnowledgeBases()
      }
    } catch (error) {
      console.error('更新知识库失败:', error)
    }
  }

  const handleOpenDeleteConfirm = (kb: KnowledgeBase, e: React.MouseEvent) => {
    e.stopPropagation()
    setDeletingKbId(kb.id)
    setShowDeleteConfirm(true)
  }

  const handleDeleteKnowledgeBase = async () => {
    try {
      const response = await knowledgeBaseApi.delete(deletingKbId)

      if (response.success) {
        setShowDeleteConfirm(false)
        if (selectedKB === deletingKbId) {
          setSelectedKB('')
        }
        loadKnowledgeBases()
      }
    } catch (error) {
      console.error('删除知识库失败:', error)
    }
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0 || !selectedKB) return

    const file = files[0]
    await handleFileUpload(file)
    
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleFileUpload = async (file: File) => {
    if (!selectedKB) return

    try {
      setUploading(true)
      const response = await documentApi.upload(file, selectedKB)

      if (response.success) {
        loadDocuments(selectedKB)
        loadKnowledgeBases()
      }
    } catch (error) {
      console.error('上传文件失败:', error)
      alert('上传文件失败，请检查文件格式')
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    const files = e.dataTransfer.files
    if (!files || files.length === 0 || !selectedKB) return

    const file = files[0]
    await handleFileUpload(file)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleOpenDeleteDocConfirm = (doc: Document, e: React.MouseEvent) => {
    e.stopPropagation()
    setDeletingDocId(doc.id)
    setShowDeleteDocConfirm(true)
  }

  const handleDeleteDocument = async () => {
    try {
      const response = await documentApi.delete(deletingDocId)

      if (response.success) {
        setShowDeleteDocConfirm(false)
        loadDocuments(selectedKB)
        loadKnowledgeBases()
      }
    } catch (error) {
      console.error('删除文件失败:', error)
    }
  }

  const handleOpenDeleteSessionConfirm = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation()
    setDeletingSessionId(session.id)
    setShowDeleteSessionConfirm(true)
  }

  const handleDeleteSession = async () => {
    try {
      const response = await chatApi.deleteSession(deletingSessionId)

      if (response.success) {
        setShowDeleteSessionConfirm(false)
        if (selectedSession === deletingSessionId) {
          setSelectedSession('')
        }
        setPinnedSessions(prev => prev.filter(id => id !== deletingSessionId))
        loadChatSessions(selectedKB)
      }
    } catch (error) {
      console.error('删除对话失败:', error)
    }
  }

  const handleTogglePinSession = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation()
    setPinnedSessions(prev => {
      if (prev.includes(session.id)) {
        return prev.filter(id => id !== session.id)
      } else {
        return [...prev, session.id]
      }
    })
  }

  const handleOpenRenameSession = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingSessionId(session.id)
    setEditingSessionTitle(session.title || '新对话')
  }

  const handleRenameSession = async () => {
    if (!editingSessionId || !editingSessionTitle.trim()) {
      setEditingSessionId('')
      return
    }

    try {
      const response = await chatApi.updateSessionTitle(editingSessionId, editingSessionTitle)

      if (response.success) {
        setEditingSessionId('')
        loadChatSessions(selectedKB)
      }
    } catch (error) {
      console.error('重命名对话失败:', error)
    }
  }

  const handleRenameKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRenameSession()
    } else if (e.key === 'Escape') {
      setEditingSessionId('')
    }
  }

  const resetForm = () => {
    setKbFormData({ name: '', description: '' })
    setEditingKbId('')
    setDeletingKbId('')
    setDeletingDocId('')
    setDeletingSessionId('')
  }

  const loadChatSessions = async (kbId: string) => {
    try {
      setSessionsLoading(true)
      const response = await chatApi.listSessions(kbId)
      if (response.success && response.data) {
        setChatSessions(response.data)
        if (response.data.length > 0 && !selectedSession) {
          setSelectedSession(response.data[0].id)
        }
      }
    } catch (error) {
      console.error('加载对话会话失败:', error)
    } finally {
      setSessionsLoading(false)
    }
  }

  const loadMessages = async (sessionId: string) => {
    try {
      setMessagesLoading(true)
      const response = await chatApi.getSessionMessages(sessionId)
      if (response.success && response.data) {
        setMessages(response.data)
      }
    } catch (error) {
      console.error('加载消息失败:', error)
    } finally {
      setMessagesLoading(false)
    }
  }

  const handleCreateNewSession = async () => {
    if (!selectedKB) return

    try {
      const response = await chatApi.createSession({
        knowledgeBaseId: selectedKB,
        title: '新对话'
      })

      if (response.success && response.data) {
        setSelectedSession(response.data.id)
        loadChatSessions(selectedKB)
      }
    } catch (error) {
      console.error('创建对话失败:', error)
    }
  }

  const handleSendMessage = async () => {
    if (!messageInput.trim() || !selectedKB || sendingMessage) return

    try {
      setSendingMessage(true)
      
      let currentSessionId = selectedSession
      
      if (!currentSessionId) {
        const createResponse = await chatApi.createSession({
          knowledgeBaseId: selectedKB,
          title: messageInput.slice(0, 30)
        })
        
        if (createResponse.success && createResponse.data) {
          currentSessionId = createResponse.data.id
          setSelectedSession(currentSessionId)
        }
      }
      
      const response = await chatApi.sendMessage({
        sessionId: currentSessionId,
        knowledgeBaseId: selectedKB,
        query: messageInput
      })

      if (response.success) {
        setMessageInput('')
        if (currentSessionId) {
          loadMessages(currentSessionId)
        }
        loadChatSessions(selectedKB)
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      alert('发送消息失败，请重试')
    } finally {
      setSendingMessage(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const currentKB = knowledgeBases.find(kb => kb.id === selectedKB)

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">localmind 知识库</h2>
          <button 
            onClick={() => { resetForm(); setShowNewKbModal(true) }}
            className="mt-2 w-full bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            + 新建知识库
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2">
          {kbLoading ? (
            <div className="p-4 text-center text-gray-500">加载中...</div>
          ) : knowledgeBases.length === 0 ? (
            <div className="p-4 text-center text-gray-500">暂无知识库，点击上方按钮创建</div>
          ) : (
            knowledgeBases.map((kb) => (
              <div
                key={kb.id}
                onClick={() => setSelectedKB(kb.id)}
                className={`p-3 rounded-lg cursor-pointer transition-colors mb-1 group ${
                  selectedKB === kb.id 
                    ? 'bg-blue-50 border border-blue-200' 
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className={`font-medium truncate ${
                      selectedKB === kb.id ? 'text-blue-700' : 'text-gray-700'
                    }`}>
                      {kb.name}
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">
                      {kb.fileCount} 个文件
                    </p>
                  </div>
                  <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                    <button
                      onClick={(e) => handleOpenEditModal(kb, e)}
                      className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-100 rounded"
                      title="编辑"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={(e) => handleOpenDeleteConfirm(kb, e)}
                      className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-100 rounded"
                      title="删除"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col bg-white">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          {currentKB ? (
            <>
              <div>
                <h2 className="text-lg font-semibold text-gray-800">
                  {currentKB.name}
                </h2>
                <p className="text-sm text-gray-500">
                  {currentKB.description || '与 AI 助手对话，基于知识库内容'}
                </p>
              </div>
              <button
                onClick={handleCreateNewSession}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                + 新建对话
              </button>
            </>
          ) : (
            <h2 className="text-lg font-semibold text-gray-800">
              请选择或创建一个知识库
            </h2>
          )}
        </div>

        <div className="flex-1 flex">
          <div className="w-64 border-r border-gray-200 flex flex-col">
            <div className="p-3 border-b border-gray-200">
              <h3 className="font-medium text-gray-700">对话历史</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-2">
              {sessionsLoading ? (
                <div className="p-4 text-center text-gray-500 text-sm">加载中...</div>
              ) : chatSessions.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-sm">
                  暂无对话，点击"新建对话"开始
                </div>
              ) : (
                <>
                  {[...chatSessions]
                    .sort((a, b) => {
                      const aPinned = pinnedSessions.includes(a.id)
                      const bPinned = pinnedSessions.includes(b.id)
                      if (aPinned && !bPinned) return -1
                      if (!aPinned && bPinned) return 1
                      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
                    })
                    .map((session) => (
                      <div
                        key={session.id}
                        onClick={() => setSelectedSession(session.id)}
                        className={`p-3 rounded-lg cursor-pointer transition-colors mb-1 group ${
                          selectedSession === session.id
                            ? 'bg-blue-50 border border-blue-200'
                            : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            {editingSessionId === session.id ? (
                              <input
                                autoFocus
                                value={editingSessionTitle}
                                onChange={(e) => setEditingSessionTitle(e.target.value)}
                                onBlur={handleRenameSession}
                                onKeyDown={handleRenameKeyPress}
                                onClick={(e) => e.stopPropagation()}
                                className="w-full px-2 py-1 text-sm border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              />
                            ) : (
                              <div className="flex items-center">
                                {pinnedSessions.includes(session.id) && (
                                  <span className="text-yellow-500 mr-1">📌</span>
                                )}
                                <p className={`font-medium text-sm truncate ${
                                  selectedSession === session.id ? 'text-blue-700' : 'text-gray-700'
                                }`}>
                                  {session.title || '新对话'}
                                </p>
                              </div>
                            )}
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(session.updatedAt).toLocaleString('zh-CN')}
                            </p>
                          </div>
                          <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                            <button
                              onClick={(e) => handleTogglePinSession(session, e)}
                              className={`p-1 rounded transition-colors ${
                                pinnedSessions.includes(session.id)
                                  ? 'text-yellow-500 bg-yellow-100'
                                  : 'text-gray-400 hover:text-yellow-500 hover:bg-yellow-100'
                              }`}
                              title={pinnedSessions.includes(session.id) ? '取消置顶' : '置顶'}
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                              </svg>
                            </button>
                            <button
                              onClick={(e) => handleOpenRenameSession(session, e)}
                              className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-100 rounded"
                              title="重命名"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                              </svg>
                            </button>
                            <button
                              onClick={(e) => handleOpenDeleteSessionConfirm(session, e)}
                              className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-100 rounded"
                              title="删除对话"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                </>
              )}
            </div>
          </div>

          <div className="flex-1 flex flex-col h-0">
            <div className="flex-1 overflow-y-auto p-4">
              {messagesLoading ? (
                <div className="text-center text-gray-500 mt-8">加载中...</div>
              ) : messages.length === 0 ? (
                <div className="text-center text-gray-500 mt-8">
                  <p className="text-lg">开始与 AI 对话吧！</p>
                  <p className="text-sm mt-2">发送您的问题，AI 会基于知识库内容回答</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[75%] ${message.role === 'user' ? 'items-end' : 'items-start'} flex`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          message.role === 'user' 
                            ? 'bg-blue-600 text-white ml-3 order-2' 
                            : 'bg-gray-200 text-gray-600 mr-3'
                        }`}>
                          {message.role === 'user' ? '👤' : '🤖'}
                        </div>
                        <div className={`p-3 rounded-lg ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-800'
                        } overflow-hidden`}>
                          <p className="whitespace-pre-wrap break-words overflow-wrap-anywhere">{message.content}</p>
                          <p className={`text-xs mt-1 ${
                            message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                          }`}>
                            {new Date(message.createdAt).toLocaleTimeString('zh-CN')}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                  {sendingMessage && (
                    <div className="flex justify-start">
                      <div className="flex items-start">
                        <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center mr-3">
                          🤖
                        </div>
                        <div className="p-3 bg-gray-100 rounded-lg">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-3">
                <textarea
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  onKeyDown={handleKeyPress}
                  disabled={!currentKB || !selectedSession || sendingMessage}
                  placeholder={!currentKB ? "请先选择知识库" : !selectedSession ? "请先选择或创建对话" : "输入您的问题..."}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 resize-none"
                  rows={2}
                />
                <button 
                  onClick={handleSendMessage}
                  disabled={!currentKB || !selectedSession || !messageInput.trim() || sendingMessage}
                  className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors disabled:bg-gray-400 self-end"
                >
                  {sendingMessage ? '发送中...' : '发送'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="w-72 bg-white border-l border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800">文件</h2>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.docx,.txt,.md,.py,.java"
            disabled={!currentKB || uploading}
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={!currentKB || uploading}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className="mt-2 w-full border-2 border-dashed border-gray-300 text-gray-500 px-4 py-3 rounded-lg text-sm font-medium hover:border-blue-500 hover:text-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? '上传中...' : '+ 上传文件'}
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2">
          {!currentKB ? (
            <div className="text-center text-gray-500 p-4">
            请先选择知识库
          </div>
          ) : docsLoading ? (
            <div className="text-center text-gray-500 p-4">
              加载中...
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center text-gray-500 p-4">
              暂无文件，点击上方按钮上传
            </div>
          ) : (
            documents.map((doc) => (
              <div key={doc.id} className="p-3 bg-gray-50 rounded-lg mb-2 group">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2 flex-1 min-w-0">
                    <span className="text-xl">{fileTypeIcons[doc.fileType] || '📄'}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-700 truncate">
                        {doc.originalName}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(doc.fileSize)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleOpenDeleteDocConfirm(doc, e)}
                    className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-100 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                    title="删除"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
                <div className="mt-2">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusColors[doc.status]}`}>
                    {statusLabels[doc.status]}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showNewKbModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              创建新知识库
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  知识库名称
                </label>
                <input
                  type="text"
                  value={kbFormData.name}
                  onChange={(e) => setKbFormData({ ...kbFormData, name: e.target.value })}
                  placeholder="请输入知识库名称"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  描述（可选）
                </label>
                <textarea
                  value={kbFormData.description}
                  onChange={(e) => setKbFormData({ ...kbFormData, description: e.target.value })}
                  placeholder="请输入知识库描述"
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => { resetForm(); setShowNewKbModal(false) }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleCreateKnowledgeBase}
                disabled={!kbFormData.name.trim()}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                创建
              </button>
            </div>
          </div>
        </div>
      )}

      {showEditKbModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              编辑知识库
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  知识库名称
                </label>
                <input
                  type="text"
                  value={kbFormData.name}
                  onChange={(e) => setKbFormData({ ...kbFormData, name: e.target.value })}
                  placeholder="请输入知识库名称"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  描述（可选）
                </label>
                <textarea
                  value={kbFormData.description}
                  onChange={(e) => setKbFormData({ ...kbFormData, description: e.target.value })}
                  placeholder="请输入知识库描述"
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => { resetForm(); setShowEditKbModal(false) }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleUpdateKnowledgeBase}
                disabled={!kbFormData.name.trim()}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                保存
              </button>
            </div>
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              确认删除
            </h3>
            <p className="text-gray-600 mb-6">
              确定要删除这个知识库吗？此操作不可撤销。
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => { resetForm(); setShowDeleteConfirm(false) }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleDeleteKnowledgeBase}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      )}

      {showDeleteDocConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              确认删除
            </h3>
            <p className="text-gray-600 mb-6">
              确定要删除这个文件吗？此操作不可撤销。
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => { resetForm(); setShowDeleteDocConfirm(false) }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleDeleteDocument}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      )}

      {showDeleteSessionConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              确认删除
            </h3>
            <p className="text-gray-600 mb-6">
              确定要删除这个对话吗？此操作不可撤销。
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => { resetForm(); setShowDeleteSessionConfirm(false) }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleDeleteSession}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
