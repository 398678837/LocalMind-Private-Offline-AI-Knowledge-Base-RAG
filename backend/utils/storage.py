
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from backend.config.settings import settings


class LocalStorage:
    """
    本地 JSON 文件存储工具类
    
    说明：
    - 所有数据存储在本地 JSON 文件中
    - 支持 CRUD 操作
    - 数据自动创建时间戳和更新时间戳
    - 确保数据安全，不会上传到任何云端
    """
    
    def __init__(self, collection_name: str):
        """
        初始化存储
        
        Args:
            collection_name: 集合名称（对应不同的数据类型，如 "knowledge_bases"）
        """
        self.collection_name = collection_name
        self.data_dir = os.path.join(settings.BASE_DATA_DIR, "storage")
        self.file_path = os.path.join(self.data_dir, f"{collection_name}.json")
        
        os.makedirs(self.data_dir, exist_ok=True)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """
        确保数据文件存在，如果不存在则创建空文件
        """
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def _read_data(self) -> Dict[str, Any]:
        """
        读取数据文件
        
        Returns:
            数据字典
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_data(self, data: Dict[str, Any]):
        """
        写入数据文件
        
        Args:
            data: 要写入的数据字典
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def generate_id(self) -> str:
        """
        生成唯一 ID
        
        Returns:
            唯一标识符
        """
        return str(uuid.uuid4())
    
    def get_all(self) -> Dict[str, Any]:
        """
        获取所有数据
        
        Returns:
            所有数据的字典
        """
        return self._read_data()
    
    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取单个数据项
        
        Args:
            item_id: 数据项 ID
            
        Returns:
            数据项字典，如果不存在则返回 None
        """
        data = self._read_data()
        return data.get(item_id)
    
    def create(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新数据项
        
        Args:
            item_data: 数据项内容
            
        Returns:
            创建后的数据项（包含 id、created_at、updated_at）
        """
        data = self._read_data()
        item_id = self.generate_id()
        now = datetime.utcnow().isoformat()
        
        item = {
            **item_data,
            "id": item_id,
            "created_at": now,
            "updated_at": now
        }
        
        data[item_id] = item
        self._write_data(data)
        
        return item
    
    def update(self, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新数据项
        
        Args:
            item_id: 数据项 ID
            item_data: 要更新的数据内容
            
        Returns:
            更新后的数据项，如果不存在则返回 None
        """
        data = self._read_data()
        
        if item_id not in data:
            return None
        
        now = datetime.utcnow().isoformat()
        
        item = {
            **data[item_id],
            **item_data,
            "id": item_id,
            "updated_at": now
        }
        
        data[item_id] = item
        self._write_data(data)
        
        return item
    
    def delete(self, item_id: str) -> bool:
        """
        删除数据项
        
        Args:
            item_id: 数据项 ID
            
        Returns:
            是否删除成功
        """
        data = self._read_data()
        
        if item_id not in data:
            return False
        
        del data[item_id]
        self._write_data(data)
        
        return True
