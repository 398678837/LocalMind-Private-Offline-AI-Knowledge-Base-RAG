
import time
from typing import List
from langchain_community.embeddings import OllamaEmbeddings
from backend.config.settings import settings


class EmbeddingGenerator:
    """文本向量化工具类 - 使用 LangChain OllamaEmbeddings"""
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_EMBEDDING_MODEL
        self._embeddings = None
        self._max_retries = 3
        self._retry_delay = 3
    
    def _get_embeddings(self) -> OllamaEmbeddings:
        """获取 LangChain OllamaEmbeddings 实例"""
        if self._embeddings is None:
            self._embeddings = OllamaEmbeddings(
                model=self.ollama_model,
                base_url=self.ollama_url
            )
        return self._embeddings
    
    def check_ollama_available(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            embeddings = self._get_embeddings()
            result = embeddings.embed_query("test")
            return result is not None and len(result) > 0
        except Exception as e:
            print(f"[WARNING] Ollama 不可用: {e}")
            return False
    
    def generate_embedding(self, text: str, retry_count: int = 0) -> List[float]:
        """生成单个文本的向量嵌入（带重试机制）"""
        try:
            embeddings = self._get_embeddings()
            embedding = embeddings.embed_query(text)
            if embedding is None or len(embedding) == 0:
                raise ValueError("Embedding 为空")
            return embedding
        except Exception as e:
            if retry_count < self._max_retries:
                print(f"[WARNING] 生成嵌入失败，{self._retry_delay}秒后重试 ({retry_count + 1}/{self._max_retries}): {e}")
                time.sleep(self._retry_delay)
                return self.generate_embedding(text, retry_count + 1)
            print(f"[ERROR] 生成嵌入失败，已达到最大重试次数: {e}")
            return []
    
    def generate_embeddings(self, texts: List[str], retry_count: int = 0) -> List[List[float]]:
        """批量生成文本向量嵌入（带重试机制）"""
        try:
            print(f"[INFO] 正在批量生成 {len(texts)} 个嵌入...")
            embeddings = self._get_embeddings()
            embedding_list = embeddings.embed_documents(texts)
            print(f"[INFO] 已完成 {len(embedding_list)}/{len(texts)} 个嵌入")
            return embedding_list
        except Exception as e:
            if retry_count < self._max_retries:
                print(f"[WARNING] 批量生成嵌入失败，{self._retry_delay}秒后重试 ({retry_count + 1}/{self._max_retries}): {e}")
                time.sleep(self._retry_delay)
                return self.generate_embeddings(texts, retry_count + 1)
            print(f"[ERROR] 批量生成嵌入失败，已达到最大重试次数: {e}")
            return []
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        try:
            import numpy as np
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            return float(similarity)
        except Exception as e:
            print(f"[ERROR] 计算相似度失败: {e}")
            return 0.0


embedding_generator = EmbeddingGenerator()
