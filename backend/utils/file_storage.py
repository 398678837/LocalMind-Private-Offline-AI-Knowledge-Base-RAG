
import os
import uuid
from pathlib import Path

from backend.config.settings import settings
from backend.models.schemas import FileType


ALLOWED_EXTENSIONS = {
    "pdf": FileType.PDF,
    "docx": FileType.DOCX,
    "txt": FileType.TXT,
    "md": FileType.MD,
    "py": FileType.PY,
    "java": FileType.JAVA
}


class FileStorage:
    """
    文件存储工具类
    
    说明：
    - 处理文件上传、存储、删除
    - 每个知识库有独立的子文件夹
    - 生成唯一文件名
    - 验证文件格式
    - 所有文件存储在本地，不上传云端
    """
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def _get_kb_upload_dir(self, knowledge_base_id):
        """
        获取知识库的上传目录
        
        Args:
            knowledge_base_id: 知识库 ID
            
        Returns:
            知识库上传目录路径
        """
        kb_upload_dir = os.path.join(self.upload_dir, knowledge_base_id)
        os.makedirs(kb_upload_dir, exist_ok=True)
        return kb_upload_dir
    
    def get_file_type(self, filename):
        """
        根据文件名获取文件类型
        
        Args:
            filename: 文件名
            
        Returns:
            文件类型枚举，如果不支持则返回 None
        """
        ext = Path(filename).suffix.lower().lstrip('.')
        return ALLOWED_EXTENSIONS.get(ext)
    
    def is_file_allowed(self, filename):
        """
        检查文件类型是否允许
        
        Args:
            filename: 文件名
            
        Returns:
            是否允许
        """
        return self.get_file_type(filename) is not None
    
    def generate_unique_filename(self, original_filename):
        """
        生成唯一的存储文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            唯一文件名（UUID + 原始扩展名）
        """
        ext = Path(original_filename).suffix.lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{ext}"
    
    def save_file(self, file_content, filename, knowledge_base_id):
        """
        保存文件到本地
        
        Args:
            file_content: 文件二进制内容
            filename: 原始文件名
            knowledge_base_id: 知识库 ID
            
        Returns:
            (存储文件名, 完整文件路径)
        """
        stored_filename = self.generate_unique_filename(filename)
        kb_upload_dir = self._get_kb_upload_dir(knowledge_base_id)
        file_path = os.path.join(kb_upload_dir, stored_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return stored_filename, file_path
    
    def delete_file(self, stored_filename, knowledge_base_id):
        """
        删除本地存储的文件
        
        Args:
            stored_filename: 存储的文件名
            knowledge_base_id: 知识库 ID
            
        Returns:
            是否删除成功
        """
        kb_upload_dir = self._get_kb_upload_dir(knowledge_base_id)
        file_path = os.path.join(kb_upload_dir, stored_filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False
    
    def get_file_path(self, stored_filename, knowledge_base_id):
        """
        获取文件的完整路径
        
        Args:
            stored_filename: 存储的文件名
            knowledge_base_id: 知识库 ID
            
        Returns:
            完整文件路径
        """
        kb_upload_dir = self._get_kb_upload_dir(knowledge_base_id)
        return os.path.join(kb_upload_dir, stored_filename)
    
    def file_exists(self, stored_filename, knowledge_base_id):
        """
        检查文件是否存在
        
        Args:
            stored_filename: 存储的文件名
            knowledge_base_id: 知识库 ID
            
        Returns:
            文件是否存在
        """
        kb_upload_dir = self._get_kb_upload_dir(knowledge_base_id)
        file_path = os.path.join(kb_upload_dir, stored_filename)
        return os.path.exists(file_path)


file_storage = FileStorage()
