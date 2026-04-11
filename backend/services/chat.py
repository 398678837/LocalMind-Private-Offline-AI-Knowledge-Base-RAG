
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from backend.utils.storage import LocalStorage
from backend.models.schemas import (
    ChatSession, ChatSessionCreate,
    ChatMessage, ChatMessageBase, MessageRole
)


class ChatService:
    """对话服务 - 会话和消息管理"""
    
    def __init__(self):
        self.session_storage = LocalStorage("chat_sessions")
        self.message_storage = LocalStorage("chat_messages")
    
    def _session_to_model(self, data: dict) -> ChatSession:
        return ChatSession(
            id=data["id"],
            knowledge_base_id=data["knowledge_base_id"],
            title=data["title"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def _message_to_model(self, data: dict) -> ChatMessage:
        return ChatMessage(
            id=data["id"],
            role=MessageRole(data["role"]),
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"])
        )
    
    def create_session(self, session_data: ChatSessionCreate) -> ChatSession:
        """创建新的对话会话"""
        item_data = {
            "knowledge_base_id": session_data.knowledge_base_id,
            "title": session_data.title or "新对话"
        }
        created = self.session_storage.create(item_data)
        return self._session_to_model(created)
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """获取对话会话"""
        data = self.session_storage.get_by_id(session_id)
        if not data:
            return None
        return self._session_to_model(data)
    
    def list_sessions(self, knowledge_base_id: Optional[str] = None) -> List[ChatSession]:
        """列出对话会话"""
        all_sessions = self.session_storage.get_all()
        sessions = []
        
        for session_dict in all_sessions.values():
            if knowledge_base_id and session_dict["knowledge_base_id"] != knowledge_base_id:
                continue
            sessions.append(self._session_to_model(session_dict))
        
        sessions.sort(key=lambda x: x.updated_at, reverse=True)
        return sessions
    
    def update_session_title(self, session_id: str, title: str) -> Optional[ChatSession]:
        """更新会话标题"""
        updated = self.session_storage.update(session_id, {"title": title})
        if not updated:
            return None
        return self._session_to_model(updated)
    
    def delete_session(self, session_id: str) -> bool:
        """删除对话会话"""
        all_messages = self.message_storage.get_all()
        for msg_id, msg_dict in list(all_messages.items()):
            if msg_dict["session_id"] == session_id:
                self.message_storage.delete(msg_id)
        return self.session_storage.delete(session_id)
    
    def add_message(self, session_id: str, role: MessageRole, content: str) -> ChatMessage:
        """添加消息"""
        item_data = {
            "session_id": session_id,
            "role": role.value,
            "content": content
        }
        created = self.message_storage.create(item_data)
        
        self.session_storage.update(session_id, {})
        
        return self._message_to_model(created)
    
    def get_messages(self, session_id: str) -> List[ChatMessage]:
        """获取会话的所有消息"""
        all_messages = self.message_storage.get_all()
        messages = []
        
        for msg_dict in all_messages.values():
            if msg_dict["session_id"] == session_id:
                messages.append(self._message_to_model(msg_dict))
        
        messages.sort(key=lambda x: x.created_at)
        return messages


chat_service = ChatService()

