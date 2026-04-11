
from typing import List, Optional
from datetime import datetime
import os
import shutil

from backend.models.schemas import (
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate
)
from backend.utils.storage import LocalStorage
from backend.config.settings import settings
from backend.utils.vector_db import vector_db


class KnowledgeBaseService:
    """
    知识库服务类
    
    说明：
    - 实现知识库的 CRUD 业务逻辑
    - 封装数据存储操作
    - 处理业务规则和验证
    """
    
    def __init__(self):
        self.storage = LocalStorage("knowledge_bases")
    
    def _to_model(self, data: dict) -> KnowledgeBase:
        """
        将存储的字典数据转换为 Pydantic 模型
        
        Args:
            data: 存储的字典数据
            
        Returns:
            KnowledgeBase 模型实例
        """
        return KnowledgeBase(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            file_count=data.get("file_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def get_all(self) -> List[KnowledgeBase]:
        """
        获取所有知识库
        
        Returns:
            知识库列表
        """
        data = self.storage.get_all()
        return [self._to_model(item) for item in data.values()]
    
    def get_by_id(self, kb_id: str) -> Optional[KnowledgeBase]:
        """
        根据 ID 获取单个知识库
        
        Args:
            kb_id: 知识库 ID
            
        Returns:
            知识库，如果不存在则返回 None
        """
        data = self.storage.get_by_id(kb_id)
        if not data:
            return None
        return self._to_model(data)
    
    def create(self, kb_create: KnowledgeBaseCreate) -> KnowledgeBase:
        """
        创建新知识库
        
        Args:
            kb_create: 创建知识库的请求数据
            
        Returns:
            创建后的知识库
        """
        item_data = {
            "name": kb_create.name,
            "description": kb_create.description,
            "file_count": 0
        }
        created = self.storage.create(item_data)
        return self._to_model(created)
    
    def update(self, kb_id: str, kb_update: KnowledgeBaseUpdate) -> Optional[KnowledgeBase]:
        """
        更新知识库
        
        Args:
            kb_id: 知识库 ID
            kb_update: 更新知识库的请求数据
            
        Returns:
            更新后的知识库，如果不存在则返回 None
        """
        item_data = {}
        
        if kb_update.name is not None:
            item_data["name"] = kb_update.name
        if kb_update.description is not None:
            item_data["description"] = kb_update.description
        
        if not item_data:
            return self.get_by_id(kb_id)
        
        updated = self.storage.update(kb_id, item_data)
        if not updated:
            return None
        
        return self._to_model(updated)
    
    def delete(self, kb_id: str) -> bool:
        """
        删除知识库
        
        Args:
            kb_id: 知识库 ID
            
        Returns:
            是否删除成功
        """
        # 删除知识库的上传文件夹
        kb_upload_dir = os.path.join(settings.UPLOAD_DIR, kb_id)
        if os.path.exists(kb_upload_dir):
            try:
                shutil.rmtree(kb_upload_dir)
                print(f"[INFO] 已删除知识库上传文件夹: {kb_upload_dir}")
            except Exception as e:
                print(f"[ERROR] 删除知识库上传文件夹失败: {e}")
        
        # 删除向量数据库中的集合
        collection_name = f"kb_{kb_id}"
        try:
            vector_db.delete_collection(collection_name)
        except Exception as e:
            print(f"[ERROR] 删除向量数据库集合失败: {e}")
        
        # 删除知识库记录
        return self.storage.delete(kb_id)
    
    def update_file_count(self, kb_id: str, delta: int) -> Optional[KnowledgeBase]:
        """
        更新知识库的文件数量
        
        Args:
            kb_id: 知识库 ID
            delta: 文件数量变化（正数增加，负数减少）
            
        Returns:
            更新后的知识库，如果不存在则返回 None
        """
        kb_data = self.storage.get_by_id(kb_id)
        if not kb_data:
            return None
        
        new_count = max(0, kb_data.get("file_count", 0) + delta)
        updated = self.storage.update(kb_id, {"file_count": new_count})
        
        if not updated:
            return None
        
        return self._to_model(updated)


knowledge_base_service = KnowledgeBaseService()
