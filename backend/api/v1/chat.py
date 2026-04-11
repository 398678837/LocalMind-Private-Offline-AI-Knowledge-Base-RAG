
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from backend.models.schemas import (
    ApiResponse, ChatRequest, ChatResponse,
    ChatSession, ChatSessionCreate, ChatSessionListResponse,
    ChatMessage, ChatMessageListResponse, MessageRole
)
from backend.services.chat import chat_service
from backend.services.rag import rag_service

router = APIRouter(prefix="/api/v1/chat", tags=["对话管理"])


@router.post("/sessions", response_model=ApiResponse)
async def create_session(session_data: ChatSessionCreate):
    """创建新的对话会话"""
    try:
        session = chat_service.create_session(session_data)
        return ApiResponse(success=True, data=session.model_dump())
    except Exception as e:
        return ApiResponse(success=False, error={"code": "CREATE_ERROR", "message": str(e)})


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(knowledge_base_id: Optional[str] = None):
    """列出对话会话"""
    try:
        sessions = chat_service.list_sessions(knowledge_base_id)
        return ChatSessionListResponse(
            success=True,
            data=[session.model_dump() for session in sessions]
        )
    except Exception as e:
        return ChatSessionListResponse(
            success=False,
            error={"code": "LIST_ERROR", "message": str(e)}
        )


@router.get("/sessions/{session_id}", response_model=ApiResponse)
async def get_session(session_id: str):
    """获取对话会话详情"""
    try:
        session = chat_service.get_session(session_id)
        if not session:
            return ApiResponse(success=False, error={"code": "NOT_FOUND", "message": "会话不存在"})
        return ApiResponse(success=True, data=session.model_dump())
    except Exception as e:
        return ApiResponse(success=False, error={"code": "GET_ERROR", "message": str(e)})


@router.put("/sessions/{session_id}/title", response_model=ApiResponse)
async def update_session_title(session_id: str, title: str):
    """更新会话标题"""
    try:
        session = chat_service.update_session_title(session_id, title)
        if not session:
            return ApiResponse(success=False, error={"code": "NOT_FOUND", "message": "会话不存在"})
        return ApiResponse(success=True, data=session.model_dump())
    except Exception as e:
        return ApiResponse(success=False, error={"code": "UPDATE_ERROR", "message": str(e)})


@router.delete("/sessions/{session_id}", response_model=ApiResponse)
async def delete_session(session_id: str):
    """删除对话会话"""
    try:
        success = chat_service.delete_session(session_id)
        if not success:
            return ApiResponse(success=False, error={"code": "NOT_FOUND", "message": "会话不存在"})
        return ApiResponse(success=True)
    except Exception as e:
        return ApiResponse(success=False, error={"code": "DELETE_ERROR", "message": str(e)})


@router.get("/sessions/{session_id}/messages", response_model=ChatMessageListResponse)
async def get_session_messages(session_id: str):
    """获取会话的所有消息"""
    try:
        messages = chat_service.get_messages(session_id)
        return ChatMessageListResponse(
            success=True,
            data=[msg.model_dump() for msg in messages]
        )
    except Exception as e:
        return ChatMessageListResponse(
            success=False,
            error={"code": "LIST_ERROR", "message": str(e)}
        )


@router.post("/send", response_model=ChatResponse)
async def send_message(chat_request: ChatRequest):
    """发送消息并获取回复（RAG 流程）"""
    try:
        # 1. 获取或创建会话
        session_id = chat_request.session_id
        if not session_id:
            session = chat_service.create_session(ChatSessionCreate(
                knowledge_base_id=chat_request.knowledge_base_id,
                title=chat_request.query[:30] if len(chat_request.query) > 30 else chat_request.query
            ))
            session_id = session.id
        
        # 2. 添加用户消息
        user_message = chat_service.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=chat_request.query
        )
        
        # 3. RAG 检索和生成回复
        response_content, retrieved_docs = rag_service.chat(
            knowledge_base_id=chat_request.knowledge_base_id,
            query=chat_request.query
        )
        
        # 4. 添加助手消息
        assistant_message = chat_service.add_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=response_content
        )
        
        return ChatResponse(success=True, data=assistant_message.model_dump())
    
    except Exception as e:
        print(f"[ERROR] 发送消息失败: {e}")
        return ChatResponse(
            success=False,
            error={"code": "CHAT_ERROR", "message": str(e)}
        )


@router.get("/ollama/status", response_model=ApiResponse)
async def check_ollama_status():
    """检查 Ollama 服务状态"""
    try:
        available = rag_service.check_ollama_available()
        return ApiResponse(success=True, data={"available": available})
    except Exception as e:
        return ApiResponse(success=False, error={"code": "CHECK_ERROR", "message": str(e)})

