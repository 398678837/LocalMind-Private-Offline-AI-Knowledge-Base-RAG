
import uuid
from typing import List, Optional
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from backend.config.settings import settings


class VectorDB:
    """向量数据库管理类 - 基于 LangChain Chroma DB"""
    
    def __init__(self):
        self.persist_directory = settings.CHROMA_DB_DIR
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_EMBEDDING_MODEL
        self._embeddings = None
    
    def _get_embeddings(self):
        """获取 LangChain OllamaEmbeddings 实例"""
        if self._embeddings is None:
            self._embeddings = OllamaEmbeddings(
                model=self.ollama_model,
                base_url=self.ollama_url
            )
        return self._embeddings
    
    def _get_vectorstore(self, collection_name: str) -> Optional[Chroma]:
        """获取或创建 Chroma 向量存储"""
        try:
            embeddings = self._get_embeddings()
            vectorstore = Chroma(
                client=chromadb.PersistentClient(path=self.persist_directory),
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=self.persist_directory
            )
            return vectorstore
        except Exception as e:
            print(f"[ERROR] 获取向量存储失败: {e}")
            return None
    
    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[dict] = None, ids: List[str] = None):
        """向知识库添加文档"""
        try:
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]
            
            if metadatas is None:
                metadatas = [{} for _ in documents]
            
            vectorstore = self._get_vectorstore(collection_name)
            if not vectorstore:
                return False
            
            vectorstore.add_texts(
                texts=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[INFO] 成功向集合 {collection_name} 添加 {len(documents)} 个文档")
            return True
        except Exception as e:
            print(f"[ERROR] 添加文档失败: {e}")
            return False
    
    def query_similar(self, collection_name: str, query_text: str = None, query_embedding: List[float] = None, n_results: int = 5) -> List[dict]:
        """检索与查询文本最相似的文档"""
        try:
            vectorstore = self._get_vectorstore(collection_name)
            if not vectorstore:
                return []
            
            if query_embedding is not None:
                print(f"[INFO] 使用预计算的嵌入向量进行检索，向量维度: {len(query_embedding)}")
                results = vectorstore.similarity_search_by_vector_with_score(
                    embedding=query_embedding,
                    k=n_results
                )
            else:
                results = vectorstore.similarity_search_with_score(
                    query=query_text,
                    k=n_results
                )
            
            combined_results = []
            for doc, score in results:
                combined_results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'distance': 1 - score,
                    'similarity': float(score)
                })
            
            print(f"[INFO] 从集合 {collection_name} 检索到 {len(combined_results)} 个相关文档")
            return combined_results
        except Exception as e:
            print(f"[ERROR] 检索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def delete_collection(self, collection_name: str):
        """删除知识库集合"""
        try:
            vectorstore = self._get_vectorstore(collection_name)
            if vectorstore:
                vectorstore.delete_collection()
                print(f"[INFO] 成功删除集合: {collection_name}")
            return True
        except Exception as e:
            print(f"[ERROR] 删除集合失败: {e}")
            return False
    
    def list_collections(self) -> List[str]:
        """列出所有集合"""
        try:
            client = chromadb.PersistentClient(path=self.persist_directory)
            collections = client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"[ERROR] 列出集合失败: {e}")
            return []
    
    def count_documents(self, collection_name: str) -> int:
        """统计集合中文档数量"""
        try:
            vectorstore = self._get_vectorstore(collection_name)
            if not vectorstore:
                return 0
            return vectorstore._collection.count()
        except Exception as e:
            print(f"[ERROR] 统计文档数量失败: {e}")
            return 0
    
    def list_all_documents(self, collection_name: str) -> dict:
        """列出集合中的所有文档（用于调试）"""
        try:
            vectorstore = self._get_vectorstore(collection_name)
            if not vectorstore:
                return {}
            
            results = vectorstore._collection.get()
            docs = results.get('documents', [])
            metadatas = results.get('metadatas', [])
            ids = results.get('ids', [])
            
            print(f"[VECTOR_DB] 集合 {collection_name} 中有 {len(docs)} 个文档")
            
            for i, (doc_id, doc, meta) in enumerate(zip(ids, docs, metadatas)):
                print(f"[VECTOR_DB] 文档 {i+1}: id={doc_id}, metadata={meta}, 内容前50字={doc[:50]}...")
            
            return results
        except Exception as e:
            print(f"[ERROR] 列出文档失败: {e}")
            return {}
    
    def delete_documents_by_document_id(self, collection_name: str, document_id: str) -> bool:
        """根据文档 ID 删除向量数据库中的相关文档"""
        try:
            print(f"\n[VECTOR_DB] ===== 开始删除文档 ID {document_id} 的向量数据 =====")
            print(f"[VECTOR_DB] 集合名称: {collection_name}")
            
            vectorstore = self._get_vectorstore(collection_name)
            if not vectorstore:
                print("[VECTOR_DB] 集合不存在")
                return False
            
            print("[VECTOR_DB] 删除前的文档:")
            self.list_all_documents(collection_name)
            
            print(f"[VECTOR_DB] 正在删除 document_id = {document_id} 的文档...")
            vectorstore._collection.delete(where={"document_id": document_id})
            
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
