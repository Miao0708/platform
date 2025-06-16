"""
知识库管理相关API端点
"""
import os
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_knowledge_base import knowledge_base, document, document_chunk
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse,
    DocumentResponse, DocumentUploadResponse, DocumentChunkResponse,
    RAGSearchRequest, RAGSearchResponse, DocumentProcessingStatus,
    KnowledgeBaseStats
)
from app.services.rag_service import rag_service
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=KnowledgeBaseResponse)
def create_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_in: KnowledgeBaseCreate
):
    """创建知识库"""
    try:
        # 检查名称是否已存在
        existing_kb = knowledge_base.get_by_name(db, name=kb_in.name)
        if existing_kb:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"知识库名称 '{kb_in.name}' 已存在"
            )
        
        kb = knowledge_base.create(db=db, obj_in=kb_in)
        return kb
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建知识库失败: {str(e)}"
        )


@router.get("/")
def read_knowledge_bases(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
):
    """获取知识库列表"""
    if active_only:
        kbs = knowledge_base.get_active_knowledge_bases(db)
    else:
        kbs = knowledge_base.get_multi(db, skip=skip, limit=limit)
    
    # 为每个知识库添加统计信息
    result = []
    for kb in kbs:
        # 获取文档统计
        doc_stats = document.get_stats_by_kb(db, kb_id=kb.id)
        
        kb_dict = {
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "collection_name": kb.collection_name,
            "embedding_model": kb.embedding_model,
            "chunk_size": kb.chunk_size,
            "chunk_overlap": kb.chunk_overlap,
            "is_active": kb.is_active,
            "created_at": kb.created_at.isoformat() if kb.created_at else None,
            "updated_at": kb.updated_at.isoformat() if kb.updated_at else None,
            "document_count": doc_stats["total_documents"],
            "total_size": doc_stats["total_size"]
        }
        result.append(kb_dict)
    
    return result


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
def read_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_id: int
):
    """获取知识库详情"""
    kb = knowledge_base.get(db=db, id=kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    return kb


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
def update_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    kb_in: KnowledgeBaseUpdate
):
    """更新知识库"""
    kb = knowledge_base.get(db=db, id=kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    
    try:
        # 如果更新名称，检查是否已存在
        update_data = kb_in.model_dump(exclude_unset=True)
        if "name" in update_data:
            existing_kb = knowledge_base.get_by_name(db, name=update_data["name"])
            if existing_kb and existing_kb.id != kb_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"知识库名称 '{update_data['name']}' 已存在"
                )
        
        kb = knowledge_base.update(db=db, db_obj=kb, obj_in=kb_in)
        return kb
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新知识库失败: {str(e)}"
        )


@router.delete("/{kb_id}")
def delete_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_id: int
):
    """删除知识库"""
    kb = knowledge_base.get(db=db, id=kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    
    try:
        knowledge_base.remove(db=db, id=kb_id)
        return {"message": "知识库删除成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除知识库失败: {str(e)}"
        )


@router.get("/{kb_id}/stats", response_model=KnowledgeBaseStats)
def get_knowledge_base_stats(
    *,
    db: Session = Depends(get_db),
    kb_id: int
):
    """获取知识库统计信息"""
    kb = knowledge_base.get(db=db, id=kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    
    try:
        # 获取统计信息
        doc_stats = document.get_stats_by_kb(db, kb_id=kb_id)
        chunk_stats = document_chunk.get_stats_by_kb(db, kb_id=kb_id)
        
        # 支持的文件类型
        supported_types = [".pdf", ".txt", ".md", ".docx", ".doc"]
        
        return KnowledgeBaseStats(
            knowledge_base_id=kb_id,
            total_documents=doc_stats["total_documents"],
            total_chunks=chunk_stats["total_chunks"],
            total_size=doc_stats["total_size"],
            processing_documents=doc_stats["processing_documents"],
            failed_documents=doc_stats["failed_documents"],
            supported_file_types=supported_types
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.post("/{kb_id}/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """上传文档到知识库"""
    # 验证知识库存在
    kb = knowledge_base.get(db=db, id=kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    
    if not kb.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="知识库未激活"
        )
    
    # 验证文件类型
    allowed_types = [".pdf", ".txt", ".md", ".docx", ".doc"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file_ext}"
        )
    
    # 验证文件大小
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制: {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # 使用文档服务处理上传
        from app.services.document_service import document_service
        
        doc = await document_service.upload_document(
            db=db,
            knowledge_base_id=kb_id,
            file=file,
            metadata=metadata
        )
        
        return DocumentUploadResponse(
            id=doc.id,
            filename=doc.filename,
            original_filename=doc.original_filename,
            file_size=doc.file_size,
            file_type=doc.file_type,
            status=doc.status,
            created_at=doc.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文档失败: {str(e)}"
        )


@router.get("/{kb_id}/documents")
def read_documents(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None
):
    """获取知识库文档列表"""
    # 验证知识库存在
    kb = knowledge_base.get(db=db, id=kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    
    try:
        if status_filter:
            docs = document.get_by_status(db, status=status_filter)
            # 过滤属于当前知识库的文档
            docs = [doc for doc in docs if doc.knowledge_base_id == kb_id]
        else:
            docs = document.get_by_knowledge_base(db, kb_id=kb_id)
        
        # 应用分页
        docs = docs[skip:skip + limit]
        
        # 转换为响应格式，确保file_size有值
        doc_list = []
        for doc in docs:
            doc_dict = {
                "id": doc.id,
                "knowledge_base_id": doc.knowledge_base_id,
                "filename": doc.filename,
                "original_filename": doc.original_filename,
                "file_path": doc.file_path,
                "file_size": doc.file_size if doc.file_size is not None else 0,
                "file_type": doc.file_type,
                "content_hash": doc.content_hash,
                "status": doc.status,
                "error_message": doc.error_message,
                "doc_metadata": doc.doc_metadata,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else None
            }
            doc_list.append(doc_dict)
        
        return doc_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档列表失败: {str(e)}"
        )


@router.post("/{kb_id}/search", response_model=RAGSearchResponse)
def search_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    search_request: RAGSearchRequest
):
    """在知识库中搜索"""
    # 验证知识库存在
    kb = knowledge_base.get(db=db, id=kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在"
        )
    
    if not kb.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="知识库未激活"
        )
    
    try:
        # 设置知识库ID
        search_request.knowledge_base_id = kb_id
        
        # 执行搜索
        response = rag_service.search_knowledge_base(db, search_request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )
