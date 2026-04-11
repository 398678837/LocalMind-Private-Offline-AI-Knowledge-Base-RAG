
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ApiResponse(BaseModel):
    """
    通用 API 响应模型
    
    说明：
    - 所有 API 响应统一使用此格式
    - success: 表示请求是否成功
    - data: 成功时返回的数据
    - error: 失败时返回的错误信息
    """
    success: bool
    data: Optional[object] = None
    error: Optional[dict] = None


class ErrorDetail(BaseModel):
    """
    错误详情模型
    """
    code: str
    message: str


class KnowledgeBaseBase(BaseModel):
    """
    知识库基础模型
    
    说明：
    - 用于创建和更新知识库时的请求体
    - name: 知识库名称，必填
    - description: 知识库描述，可选
    """
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, max_length=500, description="知识库描述")


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """
    创建知识库请求模型
    """
    pass


class KnowledgeBaseUpdate(KnowledgeBaseBase):
    """
    更新知识库请求模型
    
    说明：
    - 允许部分更新，所有字段都是可选的
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class KnowledgeBase(KnowledgeBaseBase):
    """
    知识库响应模型
    
    说明：
    - 用于返回知识库详情
    - id: 知识库唯一标识
    - file_count: 关联的文件数量
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    id: str
    file_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeBaseListResponse(ApiResponse):
    """
    知识库列表响应
    """
    data: Optional[List[KnowledgeBase]] = None


class KnowledgeBaseResponse(ApiResponse):
    """
    单个知识库响应
    """
    data: Optional[KnowledgeBase] = None


# ========================================
# 文件管理相关模型
# ========================================

class FileStatus(str, Enum):
    """
    文件状态枚举
    
    说明：
    - uploaded: 已上传，等待处理
    - processing: 处理中（解析+分块+向量化）
    - processed: 处理完成
    - error: 处理失败
    """
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"


class FileType(str, Enum):
    """
    文件类型枚举
    
    说明：
    - 支持的文件类型
    """
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    PY = "py"
    JAVA = "java"


class DocumentBase(BaseModel):
    """
    文档基础模型
    """
    name: str = Field(..., description="文件存储名称")
    original_name: str = Field(..., description="原始文件名")
    file_type: FileType = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小（字节）")
    knowledge_base_id: str = Field(..., description="关联的知识库ID")
    status: FileStatus = Field(default=FileStatus.UPLOADED, description="文件状态")
    status_message: Optional[str] = Field(None, description="状态描述信息")
    chunk_count: int = Field(default=0, description="文档分块数量")


class DocumentCreate(BaseModel):
    """
    创建文档请求模型（内部使用，不直接暴露给API）
    """
    name: str
    original_name: str
    file_type: FileType
    file_size: int
    knowledge_base_id: str


class Document(DocumentBase):
    """
    文档响应模型
    """
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(ApiResponse):
    """
    文档列表响应
    """
    data: Optional[List[Document]] = None


class DocumentResponse(ApiResponse):
    """
    单个文档响应
    """
    data: Optional[Document] = None


# ========================================
# 对话相关模型
# ========================================

class MessageRole(str, Enum):
    """
    消息角色枚举
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessageBase(BaseModel):
    """
    聊天消息基础模型
    """
    role: MessageRole
    content: str


class ChatMessage(ChatMessageBase):
    """
    聊天消息响应模型
    """
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    """
    对话会话基础模型
    """
    knowledge_base_id: str
    title: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    """
    创建对话会话请求模型
    """
    pass


class ChatSession(ChatSessionBase):
    """
    对话会话响应模型
    """
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """
    聊天请求模型
    """
    session_id: Optional[str] = None
    knowledge_base_id: str
    query: str
    stream: bool = False


class ChatResponse(ApiResponse):
    """
    聊天响应模型
    """
    data: Optional[ChatMessage] = None


class ChatSessionListResponse(ApiResponse):
    """
    对话会话列表响应
    """
    data: Optional[List[ChatSession]] = None


class ChatMessageListResponse(ApiResponse):
    """
    聊天消息列表响应
    """
    data: Optional[List[ChatMessage]] = None


class RetrievedDocument(BaseModel):
    """
    检索到的文档片段
    """
    content: str
    metadata: dict
    similarity: float
