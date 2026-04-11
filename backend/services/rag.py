
import requests
import json
from typing import List, Optional
from backend.config.settings import settings
from backend.utils.vector_db import vector_db
from backend.models.schemas import RetrievedDocument


class RAGService:
    """RAG 服务 - 检索增强生成"""
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
    
    def check_ollama_available(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"[WARNING] Ollama 不可用: {e}")
            return False
    
    def retrieve_documents(self, knowledge_base_id: str, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """从向量数据库检索相关文档"""
        try:
            collection_name = f"kb_{knowledge_base_id}"
            print(f"[RAG] 正在从集合 {collection_name} 检索文档，查询: {query}")
            
            doc_count = vector_db.count_documents(collection_name)
            print(f"[RAG] 集合 {collection_name} 中有 {doc_count} 个文档")
            
            results = vector_db.query_similar(
                collection_name=collection_name,
                query_text=query,
                n_results=top_k
            )
            
            print(f"[RAG] 检索到 {len(results)} 个相关文档")
            for i, result in enumerate(results):
                print(f"[RAG] 文档 {i+1}: 相似度={result['similarity']:.2f}, 内容前100字={result['content'][:100]}...")
            
            retrieved_docs = []
            for result in results:
                retrieved_docs.append(RetrievedDocument(
                    content=result['content'],
                    metadata=result['metadata'],
                    similarity=result['similarity']
                ))
            
            return retrieved_docs
        except Exception as e:
            print(f"[ERROR] 检索文档失败: {e}")
            return []
    
    def build_prompt(self, query: str, retrieved_docs: List[RetrievedDocument]) -> str:
        """构建 RAG 提示词"""
        context = "\n\n".join([
            f"文档片段 {i+1} (相似度: {doc.similarity:.2f}):\n{doc.content}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        prompt = f"""你是 LocalMind AI 助手，一个专业的本地知识库问答助手。请根据以下提供的文档片段来回答用户的问题。

文档片段：
{context}

用户问题：{query}

回答要求：
1. 基于提供的文档片段回答问题
2. 如果文档片段中没有相关信息，请明确说明
3. 回答要简洁、准确、有条理
4. 不要编造文档中没有的信息"""
        
        print(f"[RAG] 构建的提示词:\n{prompt}\n")
        return prompt
    
    def generate_response(self, prompt: str) -> str:
        """调用 Ollama 生成回复"""
        try:
            if not self.check_ollama_available():
                return "抱歉，本地 LLM 服务（Ollama）未启动，请先启动 Ollama 后再试。"
            
            print(f"[RAG] 正在调用 Ollama 模型: {self.ollama_model}")
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "抱歉，生成回复时出错。")
                print(f"[RAG] Ollama 生成的回复:\n{response_text}\n")
                return response_text
            else:
                error_msg = f"抱歉，LLM 服务返回错误: {response.status_code}"
                print(f"[RAG] {error_msg}")
                return error_msg
        
        except requests.exceptions.Timeout:
            return "抱歉，生成回复超时，请稍后再试。"
        except Exception as e:
            print(f"[ERROR] 生成回复失败: {e}")
            return f"抱歉，生成回复时出错: {str(e)}"
    
    def chat(self, knowledge_base_id: str, query: str) -> tuple[str, List[RetrievedDocument]]:
        """完整的 RAG 聊天流程"""
        print(f"\n[RAG] ===== 开始 RAG 聊天流程 =====")
        print(f"[RAG] 知识库 ID: {knowledge_base_id}")
        print(f"[RAG] 用户查询: {query}")
        
        # 1. 检索相关文档
        retrieved_docs = self.retrieve_documents(knowledge_base_id, query)
        print(f"[RAG] 检索到 {len(retrieved_docs)} 个文档")
        
        # 2. 构建提示词
        if retrieved_docs:
            prompt = self.build_prompt(query, retrieved_docs)
        else:
            prompt = f"用户问题：{query}\n\n注意：知识库中没有找到相关文档，请直接回答用户问题。"
            print(f"[RAG] 没有检索到文档，使用简单提示词")
        
        # 3. 生成回复
        response = self.generate_response(prompt)
        
        print(f"[RAG] ===== RAG 聊天流程结束 =====\n")
        return response, retrieved_docs


rag_service = RAGService()

