
import requests
import numpy as np
from backend.config.settings import settings


class EmbeddingGenerator:
    """文本向量化工具类 - 使用 Ollama 专门的嵌入模型"""
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_EMBEDDING_MODEL
    
    def _check_ollama_available(self):
        """检查 Ollama 是否可用"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"[WARNING] Ollama 不可用: {e}")
            return False
    
    def generate_embedding(self, text):
        """生成单个文本的向量嵌入"""
        try:
            if not self._check_ollama_available():
                print("[ERROR] Ollama 不可用，无法生成嵌入")
                return None
            
            payload = {
                "model": self.ollama_model,
                "prompt": text
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding")
                if embedding:
                    return embedding
                else:
                    print("[ERROR] Ollama 返回的嵌入为空")
                    return None
            else:
                print(f"[ERROR] Ollama 嵌入 API 返回错误: {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            print("[ERROR] 生成嵌入超时")
            return None
        except Exception as e:
            print(f"[ERROR] 生成嵌入失败: {e}")
            return None
    
    def generate_embeddings(self, texts):
        """批量生成文本向量嵌入"""
        try:
            print(f"[INFO] 正在批量生成 {len(texts)} 个嵌入...")
            embeddings = []
            for i, text in enumerate(texts):
                embedding = self.generate_embedding(text)
                if embedding:
                    embeddings.append(embedding)
                    if (i + 1) % 10 == 0:
                        print(f"[INFO] 已生成 {i + 1}/{len(texts)} 个嵌入")
                else:
                    print(f"[WARNING] 第 {i + 1} 个文本嵌入生成失败")
                    # 生成一个随机嵌入作为后备
                    random_embedding = np.random.randn(384).tolist()
                    embeddings.append(random_embedding)
            
            return embeddings
        
        except Exception as e:
            print(f"[ERROR] 批量生成嵌入失败: {e}")
            return None
    
    def compute_similarity(self, embedding1, embedding2):
        """计算两个向量的余弦相似度"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            return float(similarity)
        except Exception as e:
            print(f"[ERROR] 计算相似度失败: {e}")
            return 0.0


embedding_generator = EmbeddingGenerator()
