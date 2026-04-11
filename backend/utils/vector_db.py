

import chromadb
from backend.config.settings import settings


class VectorDB:
    """向量数据库管理类 - 基于 Chroma DB（延迟初始化）"""
    
    def __init__(self):
        self.persist_directory = settings.CHROMA_DB_DIR
        self.client = None
        self._initialized = False
    
    def _init_client(self):
        """延迟初始化 Chroma 客户端"""
        if not self._initialized:
            print("[INFO] 正在初始化 Chroma 向量数据库...")
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            print(f"[INFO] Chroma DB 初始化完成，存储路径: {self.persist_directory}")
            self._initialized = True
    
    def get_or_create_collection(self, collection_name):
        """获取或创建知识库集合"""
        try:
            self._init_client()
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": f"知识库: {collection_name}"}
            )
            return collection
        except Exception as e:
            print(f"[ERROR] 获取/创建集合失败: {e}")
            return None
    
    def add_documents(self, collection_name, documents, metadatas=None, ids=None):
        """向知识库添加文档"""
        try:
            from backend.utils.embedding import embedding_generator
            
            self._init_client()
            collection = self.get_or_create_collection(collection_name)
            if not collection:
                return False
            
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]
            
            embeddings = embedding_generator.generate_embeddings(documents)
            
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[INFO] 成功向集合 {collection_name} 添加 {len(documents)} 个文档")
            return True
        except Exception as e:
            print(f"[ERROR] 添加文档失败: {e}")
            return False
    
    def query_similar(self, collection_name, query_text, n_results=5):
        """检索与查询文本最相似的文档"""
        try:
            from backend.utils.embedding import embedding_generator
            
            self._init_client()
            collection = self.get_or_create_collection(collection_name)
            if not collection:
                return []
            
            query_embedding = embedding_generator.generate_embedding(query_text)
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            combined_results = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                combined_results.append({
                    'content': doc,
                    'metadata': meta,
                    'distance': dist,
                    'similarity': 1.0 - dist
                })
            
            return combined_results
        except Exception as e:
            print(f"[ERROR] 检索失败: {e}")
            return []
    
    def delete_collection(self, collection_name):
        """删除知识库集合"""
        try:
            self._init_client()
            self.client.delete_collection(name=collection_name)
            print(f"[INFO] 成功删除集合: {collection_name}")
            return True
        except Exception as e:
            print(f"[ERROR] 删除集合失败: {e}")
            return False
    
    def list_collections(self):
        """列出所有集合"""
        try:
            self._init_client()
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"[ERROR] 列出集合失败: {e}")
            return []
    
    def count_documents(self, collection_name):
        """统计集合中文档数量"""
        try:
            self._init_client()
            collection = self.get_or_create_collection(collection_name)
            if not collection:
                return 0
            return collection.count()
        except Exception as e:
            print(f"[ERROR] 统计文档数量失败: {e}")
            return 0
    
    def list_all_documents(self, collection_name):
        """
        列出集合中的所有文档（用于调试）
        
        Args:
            collection_name: 集合名称
            
        Returns:
            文档列表
        """
        try:
            self._init_client()
            collection = self.get_or_create_collection(collection_name)
            if not collection:
                return []
            
            results = collection.get()
            print(f"[VECTOR_DB] 集合 {collection_name} 中有 {len(results.get('ids', []))} 个文档")
            
            for i, (doc_id, doc, meta) in enumerate(zip(
                results.get('ids', []),
                results.get('documents', []),
                results.get('metadatas', [])
            )):
                print(f"[VECTOR_DB] 文档 {i+1}: id={doc_id}, metadata={meta}, 内容前50字={doc[:50]}...")
            
            return results
        except Exception as e:
            print(f"[ERROR] 列出文档失败: {e}")
            return []
    
    def delete_documents_by_document_id(self, collection_name, document_id):
        """
        根据文档 ID 删除向量数据库中的相关文档
        
        Args:
            collection_name: 集合名称
            document_id: 文档 ID
            
        Returns:
            是否删除成功
        """
        try:
            print(f"\n[VECTOR_DB] ===== 开始删除文档 ID {document_id} 的向量数据 =====")
            print(f"[VECTOR_DB] 集合名称: {collection_name}")
            
            self._init_client()
            collection = self.get_or_create_collection(collection_name)
            if not collection:
                print("[VECTOR_DB] 集合不存在")
                return False
            
            # 先列出删除前的文档
            print("[VECTOR_DB] 删除前的文档:")
            self.list_all_documents(collection_name)
            
            # 使用 where 条件删除 document_id 匹配的文档
            print(f"[VECTOR_DB] 正在删除 document_id = {document_id} 的文档...")
            collection.delete(
                where={"document_id": document_id}
            )
            
            # 列出删除后的文档
            print("[VECTOR_DB] 删除后的文档:")
            self.list_all_documents(collection_name)
            
            print(f"[INFO] 成功从集合 {collection_name} 删除文档 ID {document_id} 的相关向量数据")
            print(f"[VECTOR_DB] ===== 删除完成 =====\n")
            return True
        except Exception as e:
            print(f"[ERROR] 删除向量数据库文档失败: {e}")
            import traceback
            traceback.print_exc()
            return False


vector_db = VectorDB()

