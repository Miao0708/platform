"""
需求管理系统API端点 - 基于新的需求文档模型
"""
import os
import time
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlmodel import Session

from app.api.v1.deps import get_db
from app.crud.crud_requirement import requirement_document, requirement_analysis_task, requirement_test_task
from app.schemas.requirement import (
    RequirementDocumentCreate, RequirementDocumentUpdate, RequirementDocumentResponse,
    RequirementAnalysisTaskCreate, RequirementAnalysisTaskResponse,
    RequirementTestTaskCreate, RequirementTestTaskResponse,
    FileUploadResponse, RequirementDocumentListParams, RequirementTestTaskListParams
)
from app.core.response import StandardJSONResponse
from app.core.config import settings
from app.services.requirement_service import requirement_task_service
from app.utils.file_processor import FileProcessor

router = APIRouter()


# ===== 需求文档管理 =====
@router.get("/documents", tags=["需求管理"], response_model=List[RequirementDocumentResponse])
def get_requirement_documents(
    status: Optional[str] = Query(None, description="状态筛选：pending, processing, completed, failed"),
    skip: int = Query(0, description="跳过记录数"),
    limit: int = Query(20, description="返回记录数限制"),
    db: Session = Depends(get_db)
):
    """获取需求文档列表"""
    try:
        documents = requirement_document.get_multi_with_filter(
            db, status=status, skip=skip, limit=limit
        )
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取需求文档列表失败: {str(e)}"
        )


@router.post("/documents", tags=["需求管理"], response_model=RequirementDocumentResponse)
def create_requirement_document(
    *,
    db: Session = Depends(get_db),
    requirement_in: RequirementDocumentCreate
):
    """创建需求文档（手动输入）"""
    try:
        requirement_doc = requirement_document.create(db=db, obj_in=requirement_in)
        
        # 如果有prompt和模型配置，且内容不为空，自动启动分析任务
        if (requirement_doc.prompt_template_id and 
            requirement_doc.model_config_id and 
            requirement_doc.original_content.strip()):
            
            # 创建分析任务
            task_data = RequirementAnalysisTaskCreate(
                requirement_document_id=requirement_doc.id,
                prompt_template_id=requirement_doc.prompt_template_id,
                model_config_id=requirement_doc.model_config_id
            )
            analysis_task = requirement_analysis_task.create(db, obj_in=task_data)
            
            # 启动后台任务
            requirement_task_service.start_requirement_analysis_task(analysis_task.id)
            
            # 更新需求文档状态为处理中
            requirement_document.update_status(
                db, requirement_id=requirement_doc.id, status="processing"
            )
        
        return requirement_doc
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建需求文档失败: {str(e)}"
        )


@router.post("/documents/upload", tags=["需求管理"], response_model=RequirementDocumentResponse)
async def upload_requirement_file(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    name: str = Form(..., description="需求名称"),
    prompt_template_id: Optional[int] = Form(None, description="Prompt模板ID"),
    model_config_id: Optional[int] = Form(None, description="AI模型配置ID")
):
    """上传需求文件"""
    # 验证文件类型
    if not FileProcessor.is_supported_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型。支持的类型: {', '.join(FileProcessor.SUPPORTED_EXTENSIONS)}"
        )
    
    # 验证文件大小
    if file.size and file.size > FileProcessor.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制 ({FileProcessor.MAX_FILE_SIZE / 1024 / 1024:.1f}MB)"
        )
    
    try:
        # 创建上传目录
        upload_dir = os.path.join(settings.UPLOAD_DIR, "requirements")
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{int(time.time())}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 创建需求文档记录
        requirement_data = RequirementDocumentCreate(
            name=name,
            original_content="",  # 先创建空内容，后续由后台任务填充
            source="upload",
            original_filename=file.filename,
            file_type=FileProcessor.get_file_type(file.filename),
            prompt_template_id=prompt_template_id,
            model_config_id=model_config_id
        )
        
        requirement_doc = requirement_document.create(db=db, obj_in=requirement_data)
        
        # 启动文件处理任务
        requirement_task_service.start_file_processing_task(requirement_doc.id, file_path)
        
        return requirement_doc
        
    except Exception as e:
        # 清理已上传的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {str(e)}"
        )


@router.get("/documents/{document_id}", tags=["需求管理"], response_model=RequirementDocumentResponse)
def get_requirement_document(
    *,
    db: Session = Depends(get_db),
    document_id: int
):
    """获取需求文档详情"""
    requirement_doc = requirement_document.get(db, id=document_id)
    if not requirement_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="需求文档不存在"
        )
    return requirement_doc


@router.put("/documents/{document_id}", tags=["需求管理"], response_model=RequirementDocumentResponse)
def update_requirement_document(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    requirement_in: RequirementDocumentUpdate
):
    """更新需求文档"""
    requirement_doc = requirement_document.get(db, id=document_id)
    if not requirement_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="需求文档不存在"
        )
    
    try:
        updated_doc = requirement_document.update(db, db_obj=requirement_doc, obj_in=requirement_in)
        return updated_doc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新需求文档失败: {str(e)}"
        )


@router.delete("/documents/{document_id}", tags=["需求管理"])
def delete_requirement_document(
    *,
    db: Session = Depends(get_db),
    document_id: int
):
    """删除需求文档"""
    requirement_doc = requirement_document.get(db, id=document_id)
    if not requirement_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="需求文档不存在"
        )
    
    try:
        requirement_document.remove(db, id=document_id)
        return {"message": "需求文档删除成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除需求文档失败: {str(e)}"
        )


# ===== 需求分析任务管理 =====
@router.post("/documents/{document_id}/analyze", tags=["需求分析"], response_model=RequirementAnalysisTaskResponse)
def create_requirement_analysis_task(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    task_in: RequirementAnalysisTaskCreate
):
    """创建需求分析任务"""
    # 验证需求文档是否存在
    requirement_doc = requirement_document.get(db, id=document_id)
    if not requirement_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="需求文档不存在"
        )
    
    try:
        # 设置关联的需求文档ID
        task_in.requirement_document_id = document_id
        
        # 创建分析任务
        analysis_task = requirement_analysis_task.create(db, obj_in=task_in)
        
        # 启动后台任务
        requirement_task_service.start_requirement_analysis_task(analysis_task.id)
        
        return analysis_task
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建需求分析任务失败: {str(e)}"
        )


@router.get("/documents/{document_id}/analysis", tags=["需求分析"], response_model=RequirementAnalysisTaskResponse)
def get_requirement_analysis_task(
    *,
    db: Session = Depends(get_db),
    document_id: int
):
    """获取需求文档的分析任务"""
    analysis_task = requirement_analysis_task.get_by_requirement_id(db, requirement_id=document_id)
    if not analysis_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到相关的分析任务"
        )
    return analysis_task


# ===== 需求测试分析管理 =====
@router.get("/test-tasks", tags=["需求测试分析"], response_model=List[RequirementTestTaskResponse])
def get_requirement_test_tasks(
    status: Optional[str] = Query(None, description="状态筛选：pending, running, completed, failed"),
    skip: int = Query(0, description="跳过记录数"),
    limit: int = Query(20, description="返回记录数限制"),
    db: Session = Depends(get_db)
):
    """获取需求测试分析任务列表"""
    try:
        tasks = requirement_test_task.get_multi_with_filter(
            db, status=status, skip=skip, limit=limit
        )
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取测试任务列表失败: {str(e)}"
        )


@router.post("/test-tasks", tags=["需求测试分析"], response_model=RequirementTestTaskResponse)
def create_requirement_test_task(
    *,
    db: Session = Depends(get_db),
    task_in: RequirementTestTaskCreate
):
    """创建需求测试分析任务"""
    try:
        # 验证必须有需求内容（要么关联文档，要么直接输入）
        if not task_in.requirement_id and not task_in.requirement_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供需求文档ID或直接输入需求内容"
            )
        
        # 如果关联了需求文档，验证其存在性
        if task_in.requirement_id:
            requirement_doc = requirement_document.get(db, id=task_in.requirement_id)
            if not requirement_doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="关联的需求文档不存在"
                )
        
        # 创建测试任务
        test_task = requirement_test_task.create(db, obj_in=task_in)
        
        # 启动后台任务
        requirement_task_service.start_requirement_test_task(test_task.id)
        
        return test_task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建测试任务失败: {str(e)}"
        )


@router.get("/test-tasks/{task_id}", tags=["需求测试分析"], response_model=RequirementTestTaskResponse)
def get_requirement_test_task(
    *,
    db: Session = Depends(get_db),
    task_id: int
):
    """获取需求测试分析任务详情"""
    test_task = requirement_test_task.get(db, id=task_id)
    if not test_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试任务不存在"
        )
    return test_task


@router.delete("/test-tasks/{task_id}", tags=["需求测试分析"])
def delete_requirement_test_task(
    *,
    db: Session = Depends(get_db),
    task_id: int
):
    """删除需求测试分析任务"""
    test_task = requirement_test_task.get(db, id=task_id)
    if not test_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测试任务不存在"
        )
    
    try:
        requirement_test_task.remove(db, id=task_id)
        return {"message": "测试任务删除成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除测试任务失败: {str(e)}"
        )


# ===== 工具接口 =====
@router.get("/supported-file-types", tags=["工具"])
def get_supported_file_types_api():
    """获取支持的文件类型"""
    return {
        "supported_types": FileProcessor.SUPPORTED_EXTENSIONS,
        "max_file_size_mb": FileProcessor.MAX_FILE_SIZE / 1024 / 1024
    }


@router.post("/documents/{document_id}/skip-to-optimize", tags=["需求管理"], response_model=RequirementDocumentResponse)
def skip_to_optimize_requirement(
    *,
    db: Session = Depends(get_db),
    document_id: int,
    prompt_template_id: int = Form(..., description="优化Prompt模板ID"),
    model_config_id: int = Form(..., description="AI模型配置ID")
):
    """跳过解析，直接优化需求"""
    requirement_doc = requirement_document.get(db, id=document_id)
    if not requirement_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="需求文档不存在"
        )
    
    if not requirement_doc.original_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="需求文档没有原始内容，无法优化"
        )
    
    try:
        # 更新需求文档的prompt和模型配置
        requirement_document.update(
            db, db_obj=requirement_doc, 
            obj_in={
                "prompt_template_id": prompt_template_id,
                "model_config_id": model_config_id,
                "status": "processing"
            }
        )
        
        # 创建分析任务（用于优化）
        task_data = RequirementAnalysisTaskCreate(
            requirement_document_id=document_id,
            prompt_template_id=prompt_template_id,
            model_config_id=model_config_id
        )
        analysis_task = requirement_analysis_task.create(db, obj_in=task_data)
        
        # 启动后台任务
        requirement_task_service.start_requirement_analysis_task(analysis_task.id)
        
        # 返回更新后的需求文档
        db.refresh(requirement_doc)
        return requirement_doc
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"跳过优化操作失败: {str(e)}"
        ) 