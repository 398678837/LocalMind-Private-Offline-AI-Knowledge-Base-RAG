
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    LocalMind 后端配置类
    
    说明：
    - 使用 pydantic-settings 管理配置
    - 支持从环境变量读取配置
    - 所有路径默认指向用户本地目录，确保隐私安全
    """
    
    # 应用基本配置
    APP_NAME: str = "LocalMind - 本地私有化 AI 知识库"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # CORS 配置（仅允许本地访问）
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # 本地数据存储路径（使用项目目录下的 data 文件夹）
    BASE_DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    UPLOAD_DIR: str = os.path.join(BASE_DATA_DIR, "uploads")
    CHROMA_DB_DIR: str = os.path.join(BASE_DATA_DIR, "chroma_db")
    LOG_DIR: str = os.path.join(BASE_DATA_DIR, "logs")
    
    # Ollama 配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2:7b"
    
    # 向量化模型配置（使用 Ollama 专门的嵌入模型）
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    
    # 安全配置
    ENABLE_FILE_ENCRYPTION: bool = True
    ENABLE_SENSITIVE_DETECTION: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()


def create_directories():
    """
    创建必要的本地数据目录
    
    说明：
    - 确保所有数据存储目录存在
    - 这些目录不会被提交到 Git（已在 .gitignore 中配置）
    """
    os.makedirs(settings.BASE_DATA_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)
