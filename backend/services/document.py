
from typing import List, Optional
from datetime import datetime

from backend.models.schemas import FileType, FileStatus
from backend.utils.storage import LocalStorage
from backend.utils.file_storage import file_storage
from backend.utils.document_parser import document_parser
from backend.utils.embedding import embedding_generator
from backend.utils.vector_db import vector_db
from backend.services.knowledge_base import knowledge_base_service


class DocumentService:
    """
    文档服务类
    
    说明：
    - 实现文档的 CRUD 业务逻辑
    - 处理文件上传和存储
    - 关联知识库
    - 管理文件状态
    - 集成文档解析和分块
    """
    
    def __init__(self):
        self.storage = LocalStorage("documents")
        self.chunk_storage = LocalStorage("document_chunks")
    
    def _to_model(self, data):
        """
        将存储的字典数据转换为 Pydantic 模型
        
        Args:
            data: 存储的字典数据
            
        Returns:
            Document 模型实例
        """
        from backend.models.schemas import Document
        return Document(
            id=data["id"],
            name=data["name"],
            original_name=data["original_name"],
            file_type=FileType(data["file_type"]),
            file_size=data["file_size"],
            knowledge_base_id=data["knowledge_base_id"],
            status=FileStatus(data["status"]),
            status_message=data.get("status_message"),
            chunk_count=data.get("chunk_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def get_all_by_kb_id(self, kb_id):
        """
        获取指定知识库的所有文档
        
        Args:
            kb_id: 知识库 ID
            
        Returns:
            文档列表
        """
        all_docs = self.storage.get_all()
        docs = [
            self._to_model(doc) 
            for doc in all_docs.values() 
            if doc["knowledge_base_id"] == kb_id
        ]
        return docs
    
    def get_by_id(self, doc_id):
        """
        根据 ID 获取单个文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            文档，如果不存在则返回 None
        """
        data = self.storage.get_by_id(doc_id)
        if not data:
            return None
        return self._to_model(data)
    
    def create(self, file_content, original_filename, kb_id):
        """
        创建新文档（上传文件）
        
        Args:
            file_content: 文件二进制内容
            original_filename: 原始文件名
            kb_id: 关联的知识库 ID
            
        Returns:
            创建后的文档，如果失败则返回 None
        """
        kb = knowledge_base_service.get_by_id(kb_id)
        if not kb:
            return None
        
        file_type = file_storage.get_file_type(original_filename)
        if not file_type:
            return None
        
        stored_filename, _ = file_storage.save_file(file_content, original_filename, kb_id)
        file_size = len(file_content)
        
        item_data = {
            "name": stored_filename,
            "original_name": original_filename,
            "file_type": file_type.value,
            "file_size": file_size,
            "knowledge_base_id": kb_id,
            "status": FileStatus.UPLOADED.value,
            "status_message": None,
            "chunk_count": 0
        }
        
        created = self.storage.create(item_data)
        
        knowledge_base_service.update_file_count(kb_id, 1)
        
        return self._to_model(created)
    
    def update_status(self, doc_id, status, status_message=None, chunk_count=None):
        """
        更新文档状态
        
        Args:
            doc_id: 文档 ID
            status: 新状态
            status_message: 状态描述信息
            chunk_count: 分块数量
            
        Returns:
            更新后的文档，如果不存在则返回 None
        """
        update_data = {
            "status": status.value
        }
        
        if status_message is not None:
            update_data["status_message"] = status_message
        if chunk_count is not None:
            update_data["chunk_count"] = chunk_count
        
        updated = self.storage.update(doc_id, update_data)
        if not updated:
            return None
        
        return self._to_model(updated)
    
    def delete(self, doc_id):
        """
        删除文档
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            是否删除成功
        """
        doc = self.get_by_id(doc_id)
        if not doc:
            return False
        
        # 删除本地文件
        file_storage.delete_file(doc.name, doc.knowledge_base_id)
        
        # 删除向量数据库中的相关文档
        collection_name = f"kb_{doc.knowledge_base_id}"
        vector_db.delete_documents_by_document_id(collection_name, doc_id)
        
        # 删除文档分块
        all_chunks = self.chunk_storage.get_all()
        for chunk_id, chunk_data in all_chunks.items():
            if chunk_data.get("document_id") == doc_id:
                self.chunk_storage.delete(chunk_id)
        
        # 删除文档记录
        success = self.storage.delete(doc_id)
        
        if success:
            knowledge_base_service.update_file_count(doc.knowledge_base_id, -1)
        
        return success
    
    def process_document(self, doc_id):
        """
        处理文档：解析 -> 清洗 -> 分块 -> 向量化 -> 存入向量数据库
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            是否处理成功
        """
        print(f"\n[DOC] ===== 开始处理文档 {doc_id} =====")
        
        doc = self.get_by_id(doc_id)
        if not doc:
            print(f"[DOC] 文档不存在: {doc_id}")
            return False, "文档不存在"
        
        print(f"[DOC] 文档信息: ID={doc.id}, 名称={doc.original_name}, KB={doc.knowledge_base_id}")
        
        self.update_status(doc_id, FileStatus.PROCESSING, "正在解析文档...")
        
        try:
            file_path = file_storage.get_file_path(doc.name, doc.knowledge_base_id)
            print(f"[DOC] 文件路径: {file_path}")
            if not file_path:
                self.update_status(doc_id, FileStatus.ERROR, "文件路径错误")
                return False, "文件路径错误"
            
            self.update_status(doc_id, FileStatus.PROCESSING, "正在提取文本...")
            text = document_parser.parse_document(file_path, doc.file_type)
            print(f"[DOC] 解析到的文本长度: {len(text) if text else 0}")
            if not text:
                self.update_status(doc_id, FileStatus.ERROR, "文档解析失败")
                return False, "文档解析失败"
            
            self.update_status(doc_id, FileStatus.PROCESSING, "正在清洗文本...")
            cleaned_text = document_parser.clean_text(text)
            print(f"[DOC] 清洗后的文本长度: {len(cleaned_text)}")
            
            self.update_status(doc_id, FileStatus.PROCESSING, "正在分块...")
            chunks = document_parser.split_into_chunks(cleaned_text)
            print(f"[DOC] 生成的分块数量: {len(chunks)}")
            
            self._save_chunks(doc_id, chunks)
            
            self.update_status(doc_id, FileStatus.PROCESSING, "正在向量化并存入向量数据库...")
            
            collection_name = f"kb_{doc.knowledge_base_id}"
            print(f"[DOC] 向量数据库集合名称: {collection_name}")
            
            metadatas = []
            for i, chunk_text in enumerate(chunks):
                metadatas.append({
                    "document_id": doc_id,
                    "chunk_index": i,
                    "document_name": doc.original_name
                })
            
            print(f"[DOC] 准备向 {len(chunks)} 个文档到向量数据库")
            
            success = vector_db.add_documents(
                collection_name=collection_name,
                documents=chunks,
                metadatas=metadatas
            )
            
            print(f"[DOC] 向量化成功: {success}")
            
            self.update_status(
                doc_id, 
                FileStatus.PROCESSED, 
                f"处理完成，生成 {len(chunks)} 个分块",
                chunk_count=len(chunks)
            )
            
            print(f"[DOC] ===== 文档处理完成 =====\n")
            return True, f"处理完成，生成 {len(chunks)} 个分块"
            
        except Exception as e:
            print(f"[ERROR] 处理文档失败: {e}")
            self.update_status(doc_id, FileStatus.ERROR, f"处理失败: {str(e)}")
            return False, f"处理失败: {str(e)}"
    
    def _save_chunks(self, doc_id, chunks):
        """
        保存文档分块
        
        Args:
            doc_id: 文档 ID
            chunks: 文本块列表
        """
        for i, chunk_text in enumerate(chunks):
            chunk_data = {
                "document_id": doc_id,
                "chunk_index": i,
                "text": chunk_text,
                "embedding": None
            }
            self.chunk_storage.create(chunk_data)
    
    def get_chunks_by_doc_id(self, doc_id):
        """
        获取文档的所有分块
        
        Args:
            doc_id: 文档 ID
            
        Returns:
            分块列表
        """
        all_chunks = self.chunk_storage.get_all()
        doc_chunks = [
            chunk 
            for chunk in all_chunks.values() 
            if chunk["document_id"] == doc_id
        ]
        return sorted(doc_chunks, key=lambda x: x["chunk_index"])


document_service = DocumentService()
