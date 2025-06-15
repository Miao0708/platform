"""
需求管理API端点（适配前端需求）
"""
import os
import json
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_task import requirement_parse_task
from app.schemas.task import (
    RequirementParseTaskCreate, RequirementParseTaskResponse, RequirementParseTaskUpdate
)
from app.core.response import StandardJSONResponse
from app.core.config import settings
from app.tasks.requirement_tasks import parse_requirement_text, process_requirement_file

router = APIRouter()


@router.get("", tags=["需求管理"])
def get_requirements(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取需求列表"""
    try:
        if category:
            requirements = requirement_parse_task.get_by_category(db, category=category)
        elif status_filter:
            requirements = requirement_parse_task.get_by_status(db, status=status_filter)
        elif priority:
            requirements = requirement_parse_task.get_by_priority(db, priority=priority)
        else:
            requirements = requirement_parse_task.get_multi(db, skip=skip, limit=limit)
        
        requirement_list = []
        for req in requirements:
            requirement_list.append({
                "id": str(req.id),
                "name": req.name,
                "original_content": req.original_content,
                "parsed_content": req.parsed_content,
                "structured_requirements": req.structured_requirements,
                "category": req.category,
                "priority": req.priority,
                "complexity": req.complexity,
                "estimated_hours": req.estimated_hours,
                "status": req.status,
                "input_type": req.input_type,
                "file_name": req.file_name,
                "file_size": req.file_size,
                "created_at": req.created_at.isoformat() + "Z" if req.created_at else None,
                "updated_at": req.updated_at.isoformat() + "Z" if req.updated_at else None
            })
        
        return StandardJSONResponse(
            content=requirement_list,
            message="获取需求列表成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取需求列表失败: {str(e)}"
        )


@router.post("", tags=["需求管理"])
def create_requirement(
    *,
    db: Session = Depends(get_db),
    requirement_in: RequirementParseTaskCreate
):
    """创建需求（文本输入）"""
    try:
        req = requirement_parse_task.create(db=db, obj_in=requirement_in)
        
        # 如果有文本内容，立即启动解析任务
        if req.original_content and req.original_content.strip():
            parse_requirement_text.delay(req.id)
        
        requirement_data = {
            "id": str(req.id),
            "name": req.name,
            "original_content": req.original_content,
            "category": req.category,
            "priority": req.priority,
            "status": req.status,
            "input_type": req.input_type
        }
        
        return StandardJSONResponse(
            content=requirement_data,
            message="需求创建成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"创建需求失败: {str(e)}"
        )


@router.post("/upload", tags=["需求管理"])
async def upload_requirement_file(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    name: str = Form(...),
    category: Optional[str] = Form(None),
    priority: str = Form("medium"),
    task_metadata: Optional[str] = Form(None)
):
    """上传需求文件"""
    # 验证文件类型
    allowed_types = [".txt", ".md", ".docx", ".pdf"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_types:
        return StandardJSONResponse(
            content=None,
            status_code=400,
            message=f"不支持的文件类型: {file_ext}"
        )
    
    # 验证文件大小
    if file.size and file.size > settings.MAX_FILE_SIZE:
        return StandardJSONResponse(
            content=None,
            status_code=400,
            message=f"文件大小超过限制: {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # 保存文件
        upload_dir = os.path.join(settings.UPLOAD_DIR, "requirements")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{int(time.time())}_{file.filename}")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 解析元数据
        metadata = {}
        if task_metadata:
            try:
                metadata = json.loads(task_metadata)
            except json.JSONDecodeError:
                pass
        
        # 创建任务
        task_data = RequirementParseTaskCreate(
            name=name,
            input_type="file",
            category=category,
            priority=priority,
            task_metadata=metadata
        )
        
        req = requirement_parse_task.create(db=db, obj_in=task_data)
        
        # 更新文件信息
        req.file_path = file_path
        req.file_name = file.filename
        req.file_size = len(content)
        db.add(req)
        db.commit()
        db.refresh(req)
        
        # 启动文件处理任务
        process_requirement_file.delay(req.id, file_path)
        
        requirement_data = {
            "id": str(req.id),
            "name": req.name,
            "file_name": req.file_name,
            "file_size": req.file_size,
            "category": req.category,
            "priority": req.priority,
            "status": req.status,
            "input_type": req.input_type
        }
        
        return StandardJSONResponse(
            content=requirement_data,
            message="需求文件上传成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"上传需求文件失败: {str(e)}"
        )


@router.get("/{requirement_id}", tags=["需求管理"])
def get_requirement_detail(
    *,
    db: Session = Depends(get_db),
    requirement_id: str
):
    """获取需求详情"""
    try:
        req = requirement_parse_task.get(db=db, id=int(requirement_id))
        if not req:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="需求不存在"
            )
        
        requirement_data = {
            "id": str(req.id),
            "name": req.name,
            "original_content": req.original_content,
            "parsed_content": req.parsed_content,
            "structured_requirements": req.structured_requirements,
            "category": req.category,
            "priority": req.priority,
            "complexity": req.complexity,
            "estimated_hours": req.estimated_hours,
            "status": req.status,
            "input_type": req.input_type,
            "file_name": req.file_name,
            "file_path": req.file_path,
            "file_size": req.file_size,
            "llm_model": req.llm_model,
            "tokens_used": req.tokens_used,
            "processing_time": req.processing_time,
            "error_message": req.error_message,
            "task_metadata": req.task_metadata,

        }
        
        return StandardJSONResponse(
            content=requirement_data,
            message="获取需求详情成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取需求详情失败: {str(e)}"
        )


@router.put("/{requirement_id}", tags=["需求管理"])
def update_requirement(
    *,
    db: Session = Depends(get_db),
    requirement_id: str,
    requirement_in: RequirementParseTaskUpdate
):
    """更新需求"""
    try:
        req = requirement_parse_task.get(db=db, id=int(requirement_id))
        if not req:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="需求不存在"
            )
        
        updated_req = requirement_parse_task.update(db=db, db_obj=req, obj_in=requirement_in)
        
        requirement_data = {
            "id": str(updated_req.id),
            "name": updated_req.name,
            "parsed_content": updated_req.parsed_content,
            "category": updated_req.category,
            "priority": updated_req.priority,
            "complexity": updated_req.complexity,
            "estimated_hours": updated_req.estimated_hours
        }
        
        return StandardJSONResponse(
            content=requirement_data,
            message="需求更新成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"更新需求失败: {str(e)}"
        )


@router.delete("/{requirement_id}", tags=["需求管理"])
def delete_requirement(
    *,
    db: Session = Depends(get_db),
    requirement_id: str
):
    """删除需求"""
    try:
        req = requirement_parse_task.get(db=db, id=int(requirement_id))
        if not req:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="需求不存在"
            )
        
        requirement_parse_task.remove(db=db, id=int(requirement_id))
        
        return StandardJSONResponse(
            content=None,
            message="需求删除成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"删除需求失败: {str(e)}"
        )
