
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form

from backend.models.schemas import (
    DocumentListResponse,
    DocumentResponse,
    ApiResponse
)
from backend.services.document import document_service
from backend.utils.file_storage import file_storage


router = APIRouter(prefix="/api/v1", tags=["文件管理"])


@router.post("/files/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    knowledge_base_id: str = Form(...)
):
    """
    上传文件
    
    支持的文件格式: PDF, DOCX, TXT, MD, PY, JAVA
    文件上传后自动开始解析和分块处理
    """
    if not file_storage.is_file_allowed(file.filename or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": "不支持的文件格式，仅支持 PDF、DOCX、TXT、MD、PY、JAVA"
            }
        )
    
    file_content = await file.read()
    original_filename = file.filename or "unknown"
    
    document = document_service.create(
        file_content=file_content,
        original_filename=original_filename,
        kb_id=knowledge_base_id
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_KNOWLEDGE_BASE",
                "message": "知识库不存在"
            }
        )
    
    import threading
    threading.Thread(
        target=lambda: document_service.process_document(document.id),
        daemon=True
    ).start()
    
    return DocumentResponse(
        success=True,
        data=document
    )


@router.post("/files/{file_id}/process")
async def process_document(file_id: str):
    """
    手动触发文档处理
    
    解析文档 -> 清洗文本 -> 分块 -> 存储
    """
    document = document_service.get_by_id(file_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"文件 {file_id} 不存在"
            }
        )
    
    success, message = document_service.process_document(file_id)
    
    return ApiResponse(
        success=success,
        data={"message": message}
    )


@router.get("/files/{file_id}/chunks")
async def get_document_chunks(file_id: str):
    """
    获取文档的分块列表
    """
    document = document_service.get_by_id(file_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"文件 {file_id} 不存在"
            }
        )
    
    chunks = document_service.get_chunks_by_doc_id(file_id)
    
    return ApiResponse(
        success=True,
        data={"chunks": chunks}
    )


@router.get("/knowledge-bases/{kb_id}/files")
async def get_knowledge_base_files(kb_id: str):
    """
    获取知识库的文件列表
    """
    documents = document_service.get_all_by_kb_id(kb_id)
    return DocumentListResponse(
        success=True,
        data=documents
    )


@router.get("/files/{file_id}")
async def get_file(file_id: str):
    """
    获取文件详情
    """
    document = document_service.get_by_id(file_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"文件 {file_id} 不存在"
            }
        )
    
    return DocumentResponse(
        success=True,
        data=document
    )


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    删除文件
    """
    success = document_service.delete(file_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"文件 {file_id} 不存在"
            }
        )
    
    return ApiResponse(
        success=True,
        data={"message": "文件删除成功"}
    )
