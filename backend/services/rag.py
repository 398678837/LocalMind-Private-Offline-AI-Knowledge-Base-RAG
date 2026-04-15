

import time
from typing import List, Tuple, Optional
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from backend.config.settings import settings
from backend.utils.vector_db import vector_db


class RAGService:
    """RAG 服务 - 使用 LangChain RAG Chain"""
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
        self._llm = None
        self._max_retries = 3
        self._retry_delay = 5
    
    def _get_llm(self) -> ChatOllama:
        """获取 LangChain ChatOllama 实例"""
        if self._llm is None:
            self._llm = ChatOllama(
                model=self.ollama_model,
                base_url=self.ollama_url,
                temperature=0.1,
                repeat_penalty=1.2,
                request_timeout=180
            )
        return self._llm
    
    def check_ollama_available(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            llm = self._get_llm()
            llm.invoke("hello")
            return True
        except Exception as e:
            print(f"[WARNING] Ollama 不可用: {e}")
            return False
    
    def get_retriever(self, knowledge_base_id: str, top_k: int = 5):
        """获取 LangChain 检索器"""
        try:
            from backend.utils.vector_db import vector_db
            
            collection_name = f"kb_{knowledge_base_id}"
            doc_count = vector_db.count_documents(collection_name)
            print(f"[RAG] 集合 {collection_name} 中有 {doc_count} 个文档")
            
            if doc_count == 0:
                print(f"[WARNING] 集合中没有文档")
                return None
            
            vectorstore = vector_db._get_vectorstore(collection_name)
            if not vectorstore:
                print(f"[ERROR] 无法获取向量存储")
                return None
            
            retriever = vectorstore.as_retriever(
                search_kwargs={"k": top_k}
            )
            return retriever
        except Exception as e:
            print(f"[ERROR] 获取检索器失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def build_rag_chain(self, knowledge_base_id: str, top_k: int = 5) -> Optional[RetrievalQA]:
        """构建 LangChain RAG Chain"""
        try:
            retriever = self.get_retriever(knowledge_base_id, top_k)
            if not retriever:
                return None
            
            llm = self._get_llm()
            
            prompt_template = """你是 LocalMind AI 助手，一个专业的本地知识库问答助手。请根据以下提供的文档片段来回答用户的问题。

文档片段：
{context}

用户问题：{question}

回答要求：
1. 基于提供的文档片段回答问题
2. 如果文档片段中没有相关信息，请明确说明
3. 回答要简洁、准确、有条理
4. 不要编造文档中没有的信息"""

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            rag_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )
            
            print(f"[RAG] RAG Chain 构建成功")
            return rag_chain
        except Exception as e:
            print(f"[ERROR] 构建 RAG Chain 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def chat(self, knowledge_base_id: str, query: str, top_k: int = 5) -> Tuple[str, List[dict]]:
        """完整的 RAG 聊天流程"""
        print(f"\n[RAG] ===== 开始 RAG 聊天流程 =====")
        print(f"[RAG] 知识库 ID: {knowledge_base_id}")
        print(f"[RAG] 用户查询: {query}")
        
        try:
            if not self.check_ollama_available():
                return "抱歉，本地 LLM 服务（Ollama）未启动，请先启动 Ollama 后再试。", []
            
            rag_chain = self.build_rag_chain(knowledge_base_id, top_k)
            
            if not rag_chain:
                print(f"[RAG] 没有可用的检索器，使用简单提示词")
                return self._fallback_chat(query)
            
            print(f"[RAG] 正在调用 Ollama 模型: {self.ollama_model}")
            
            result = rag_chain.invoke({"query": query})
            
            response_text = result.get("result", "")
            if hasattr(result, 'content'):
                response_text = result.content
            
            source_documents = []
            if hasattr(result, 'source_documents'):
                source_documents = result.source_documents
            elif 'source_documents' in result:
                source_documents = result['source_documents']
            
            retrieved_docs = []
            for doc in source_documents:
                retrieved_docs.append({
                    'content': doc.page_content if hasattr(doc, 'page_content') else str(doc),
                    'metadata': doc.metadata if hasattr(doc, 'metadata') else {},
                    'similarity': 1.0
                })
            
            print(f"[RAG] 检索到 {len(retrieved_docs)} 个相关文档")
            print(f"[RAG] Ollama 生成的回复:\n{response_text[:200]}...\n")
            
            print(f"[RAG] ===== RAG 聊天流程结束 =====\n")
            return response_text, retrieved_docs
            
        except Exception as e:
            print(f"[ERROR] RAG 聊天失败: {e}")
            import traceback
            traceback.print_exc()
            
            print(f"[RAG] 使用降级策略...")
            return self._fallback_chat(query)
    
    def _fallback_chat(self, query: str) -> Tuple[str, List[dict]]:
        """降级聊天（无检索时直接回答）"""
        try:
            llm = self._get_llm()
            prompt = f"用户问题：{query}\n\n请直接回答用户问题。"
            response = llm.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            print(f"[RAG] 降级策略成功")
            print(f"[RAG] ===== RAG 聊天流程结束 =====\n")
            return response_text, []
        except Exception as e2:
            print(f"[ERROR] 降级策略也失败: {e2}")
            print(f"[RAG] ===== RAG 聊天流程结束 =====\n")
            return f"抱歉，AI 服务暂时不可用，请检查 Ollama 是否正常运行。", []


rag_service = RAGService()
