
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config.settings import settings, create_directories
from backend.api.v1 import knowledge_base, document, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期管理器
    
    说明：
    - startup：应用启动时执行
    - shutdown：应用关闭时执行
    """
    # 启动时
    print(f"[INFO] 正在启动 {settings.APP_NAME} v{settings.APP_VERSION}...")
    create_directories()
    print(f"[INFO] 本地数据目录已准备就绪: {settings.BASE_DATA_DIR}")
    print(f"[INFO] {settings.APP_NAME} 启动成功！")
    yield
    # 关闭时
    print(f"[INFO] {settings.APP_NAME} 正在关闭...")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="本地私有化、隐私优先的 AI 知识库问答助手，100% 本地离线运行",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS（仅允许本地访问，确保隐私安全）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(knowledge_base.router)
app.include_router(document.router)
app.include_router(chat.router)


@app.get("/", tags=["根路径"])
async def root():
    """
    根路径接口
    
    返回应用基本信息，用于快速检查服务是否正常运行
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "message": "欢迎使用 LocalMind！所有功能均在本地离线运行，保护您的隐私安全。"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """
    健康检查接口
    
    用于监控服务健康状态，返回服务基本信息
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }


@app.get("/api/v1/status", tags=["系统状态"])
async def get_system_status():
    """
    获取系统状态接口（v1 版本）
    
    返回系统配置和状态信息，前端用于初始化
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ollama_url": settings.OLLAMA_BASE_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "file_encryption_enabled": settings.ENABLE_FILE_ENCRYPTION,
        "sensitive_detection_enabled": settings.ENABLE_SENSITIVE_DETECTION
    }


if __name__ == "__main__":
    import uvicorn
    print(f"[INFO] 启动 LocalMind 后端服务...")
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
