# LocalMind API 接口文档

## 基础信息
- **Base URL**: `http://127.0.0.1:8000`
- **API 版本**: v1
- **所有接口均本地离线运行，无云端请求**

---

## 一、知识库管理接口

### 1.1 获取知识库列表
```
GET /api/v1/knowledge-bases
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": "kb_001",
      "name": "我的文档库",
      "description": "存储我的个人文档和笔记",
      "file_count": 15,
      "created_at": "2026-04-01T10:00:00Z",
      "updated_at": "2026-04-10T15:30:00Z"
    }
  ]
}
```

---

### 1.2 创建知识库
```
POST /api/v1/knowledge-bases
```

**请求体**:
```json
{
  "name": "新技术文档",
  "description": "存储技术相关文档"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "kb_002",
    "name": "新技术文档",
    "description": "存储技术相关文档",
    "file_count": 0,
    "created_at": "2026-04-11T10:00:00Z",
    "updated_at": "2026-04-11T10:00:00Z"
  }
}
```

---

### 1.3 获取单个知识库详情
```
GET /api/v1/knowledge-bases/{kb_id}
```

**路径参数**:
- `kb_id`: 知识库ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "kb_001",
    "name": "我的文档库",
    "description": "存储我的个人文档和笔记",
    "file_count": 15,
    "created_at": "2026-04-01T10:00:00Z",
    "updated_at": "2026-04-10T15:30:00Z"
  }
}
```

---

### 1.4 更新知识库
```
PUT /api/v1/knowledge-bases/{kb_id}
```

**路径参数**:
- `kb_id`: 知识库ID

**请求体**:
```json
{
  "name": "我的文档库（已更新）",
  "description": "更新后的描述"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "kb_001",
    "name": "我的文档库（已更新）",
    "description": "更新后的描述",
    "file_count": 15,
    "created_at": "2026-04-01T10:00:00Z",
    "updated_at": "2026-04-11T11:00:00Z"
  }
}
```

---

### 1.5 删除知识库
```
DELETE /api/v1/knowledge-bases/{kb_id}
```

**路径参数**:
- `kb_id`: 知识库ID

**响应示例**:
```json
{
  "success": true,
  "message": "知识库删除成功"
}
```

---

## 二、文件管理接口

### 2.1 上传文件
```
POST /api/v1/files/upload
```

**请求体（multipart/form-data）:
- `file`: 要上传的文件
- `knowledge_base_id`: 关联的知识库ID

**支持的文件格式**:
- PDF (.pdf)
- Word (.docx)
- 纯文本 (.txt)
- Markdown (.md)
- Python (.py)
- Java (.java)

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "file_001",
    "name": "论文.pdf",
    "original_name": "我的论文.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "knowledge_base_id": "kb_001",
    "status": "uploaded",
    "created_at": "2026-04-11T10:00:00Z",
    "updated_at": "2026-04-11T10:00:00Z"
  }
}
```

---

### 2.2 获取知识库文件列表
```
GET /api/v1/knowledge-bases/{kb_id}/files
```

**路径参数**:
- `kb_id`: 知识库ID

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": "file_001",
      "name": "论文.pdf",
      "original_name": "我的论文.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "status": "processed",
      "created_at": "2026-04-11T10:00:00Z"
    }
  ]
}
```

---

### 2.3 获取文件详情
```
GET /api/v1/files/{file_id}
```

**路径参数**:
- `file_id`: 文件ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "file_001",
    "name": "论文.pdf",
    "original_name": "我的论文.pdf",
    "file_type": "pdf",
    "file_size": 1024000,
    "knowledge_base_id": "kb_001",
    "status": "processed",
    "status_message": "处理完成",
    "chunk_count": 15,
    "created_at": "2026-04-11T10:00:00Z",
    "updated_at": "2026-04-11T10:05:00Z"
  }
}
```

---

### 2.4 删除文件
```
DELETE /api/v1/files/{file_id}
```

**路径参数**:
- `file_id`: 文件ID

**响应示例**:
```json
{
  "success": true,
  "message": "文件删除成功"
}
```

---

### 文件状态说明
- `uploaded`: 已上传，等待处理
- `processing`: 处理中（解析+分块+向量化）
- `processed`: 处理完成
- `error`: 处理失败

---

## 三、AI 对话接口

### 3.1 创建会话
```
POST /api/v1/chat/sessions
```

**请求体**:
```json
{
  "title": "新对话",
  "knowledge_base_id": "kb_001"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "session_001",
    "title": "新对话",
    "knowledge_base_id": "kb_001",
    "created_at": "2026-04-11T10:00:00Z",
    "updated_at": "2026-04-11T10:00:00Z"
  }
}
```

---

### 3.2 获取会话列表
```
GET /api/v1/chat/sessions?knowledge_base_id={kb_id}
```

**查询参数**:
- `knowledge_base_id` (可选): 知识库ID，不传则返回所有会话

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": "session_001",
      "title": "新对话",
      "knowledge_base_id": "kb_001",
      "created_at": "2026-04-11T10:00:00Z",
      "updated_at": "2026-04-11T10:05:00Z"
    }
  ]
}
```

---

### 3.3 获取会话详情
```
GET /api/v1/chat/sessions/{id}
```

**路径参数**:
- `id`: 会话ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "session_001",
    "title": "新对话",
    "knowledge_base_id": "kb_001",
    "created_at": "2026-04-11T10:00:00Z",
    "updated_at": "2026-04-11T10:05:00Z"
  }
}
```

---

### 3.4 更新会话标题
```
PUT /api/v1/chat/sessions/{id}/title
```

**路径参数**:
- `id`: 会话ID

**请求体**:
```json
{
  "title": "已更新的标题"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": "session_001",
    "title": "已更新的标题",
    "created_at": "2026-04-11T10:00:00Z",
    "updated_at": "2026-04-11T10:10:00Z"
  }
}
```

---

### 3.5 删除会话
```
DELETE /api/v1/chat/sessions/{id}
```

**路径参数**:
- `id`: 会话ID

**响应示例**:
```json
{
  "success": true,
  "message": "会话删除成功"
}
```

---

### 3.6 获取会话消息列表
```
GET /api/v1/chat/sessions/{id}/messages
```

**路径参数**:
- `id`: 会话ID

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": "msg_001",
      "session_id": "session_001",
      "role": "user",
      "content": "什么是 AI？",
      "created_at": "2026-04-11T10:00:00Z"
    },
    {
      "id": "msg_002",
      "session_id": "session_001",
      "role": "assistant",
      "content": "AI（人工智能）是...",
      "created_at": "2026-04-11T10:00:10Z"
    }
  ]
}
```

---

### 3.7 发送消息（RAG 问答）
```
POST /api/v1/chat/send
```

**请求体**:
```json
{
  "knowledge_base_id": "kb_001",
  "query": "什么是 RAG？",
  "session_id": "session_001"  // 可选，不传则自动创建新会话
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_001",
    "user_message": {
      "id": "msg_001",
      "content": "什么是 RAG？",
      "role": "user",
      "created_at": "2026-04-11T10:00:00Z"
    },
    "assistant_message": {
      "id": "msg_002",
      "content": "RAG（检索增强生成）是...",
      "role": "assistant",
      "created_at": "2026-04-11T10:00:10Z"
    }
  }
}
```

---

### 3.8 检查 Ollama 状态
```
GET /api/v1/chat/ollama/status
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "available": true,
    "model": "qwen2:7b",
    "embedding_model": "nomic-embed-text:latest"
  }
}
```

---

## 四、系统配置接口

### 4.1 获取系统状态
```
GET /api/v1/status
```

**响应示例**:
```json
{
  "app_name": "LocalMind - 本地私有化 AI 知识库",
  "version": "1.0.0",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "qwen2:7b",
  "embedding_model": "nomic-embed-text:latest",
  "file_encryption_enabled": false,
  "sensitive_detection_enabled": false
}
```

---

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "data": {...}
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

### 错误码说明
- `NOT_FOUND`: 资源不存在
- `VALIDATION_ERROR`: 请求参数验证失败
- `INTERNAL_ERROR`: 服务器内部错误
