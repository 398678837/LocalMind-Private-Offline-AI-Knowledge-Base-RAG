
from fastapi import APIRouter, HTTPException, status
from typing import List

from backend.models.schemas import (
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseListResponse,
    KnowledgeBaseResponse,
    ApiResponse
)
from backend.services.knowledge_base import knowledge_base_service


router = APIRouter(prefix="/api/v1/knowledge-bases", tags=["知识库管理"])


@router.get("", response_model=KnowledgeBaseListResponse)
async def get_all_knowledge_bases():
    """
    获取所有知识库列表
    
    Returns:
        知识库列表
    """
    knowledge_bases = knowledge_base_service.get_all()
    return KnowledgeBaseListResponse(
        success=True,
        data=knowledge_bases
    )


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(kb_id: str):
    """
    获取单个知识库详情
    
    Args:
        kb_id: 知识库 ID
        
    Returns:
        知识库详情
        
    Raises:
        HTTPException: 知识库不存在时返回 404
    """
    knowledge_base = knowledge_base_service.get_by_id(kb_id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"知识库 {kb_id} 不存在"
            }
        )
    
    return KnowledgeBaseResponse(
        success=True,
        data=knowledge_base
    )


@router.post("", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(kb_create: KnowledgeBaseCreate):
    """
    创建新知识库
    
    Args:
        kb_create: 创建知识库的请求数据
        
    Returns:
        创建后的知识库
    """
    knowledge_base = knowledge_base_service.create(kb_create)
    return KnowledgeBaseResponse(
        success=True,
        data=knowledge_base
    )


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(kb_id: str, kb_update: KnowledgeBaseUpdate):
    """
    更新知识库
    
    Args:
        kb_id: 知识库 ID
        kb_update: 更新知识库的请求数据
        
    Returns:
        更新后的知识库
        
    Raises:
        HTTPException: 知识库不存在时返回 404
    """
    knowledge_base = knowledge_base_service.update(kb_id, kb_update)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"知识库 {kb_id} 不存在"
            }
        )
    
    return KnowledgeBaseResponse(
        success=True,
        data=knowledge_base
    )


@router.delete("/{kb_id}", response_model=ApiResponse)
async def delete_knowledge_base(kb_id: str):
    """
    删除知识库
    
    Args:
        kb_id: 知识库 ID
        
    Returns:
        删除成功的响应
        
    Raises:
        HTTPException: 知识库不存在时返回 404
    """
    success = knowledge_base_service.delete(kb_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": f"知识库 {kb_id} 不存在"
            }
        )
    
    return ApiResponse(
        success=True,
        data={"message": "知识库删除成功"}
    )
