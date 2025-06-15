"""
Prompt模板相关API端点
"""
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_prompt import prompt_template
from app.schemas.prompt import (
    PromptTemplateCreate, PromptTemplateUpdate, PromptTemplateResponse,
    PromptExecuteRequest, PromptExecuteResponse,
    PromptValidateRequest, PromptValidateResponse
)
from app.services.prompt_service import prompt_service

router = APIRouter()


@router.post("/", response_model=PromptTemplateResponse)
def create_prompt_template(
    *,
    db: Session = Depends(get_db),
    template_in: PromptTemplateCreate
):
    """创建Prompt模板"""
    try:
        template = prompt_template.create(db=db, obj_in=template_in)
        return template
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建Prompt模板失败: {str(e)}"
        )


@router.get("/", response_model=List[PromptTemplateResponse])
def read_prompt_templates(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    active_only: bool = True
):
    """获取Prompt模板列表"""
    if category:
        templates = prompt_template.get_by_category(db, category=category)
    elif active_only:
        templates = prompt_template.get_active_templates(db)
    else:
        templates = prompt_template.get_multi(db, skip=skip, limit=limit)
    
    return templates


@router.get("/categories", response_model=List[str])
def read_prompt_categories(db: Session = Depends(get_db)):
    """获取所有Prompt分类"""
    categories = prompt_template.get_categories(db)
    return categories


@router.get("/search", response_model=List[PromptTemplateResponse])
def search_prompt_templates(
    *,
    db: Session = Depends(get_db),
    name: str
):
    """根据名称搜索Prompt模板"""
    templates = prompt_template.search_by_name(db, name_query=name)
    return templates


@router.get("/{template_id}", response_model=PromptTemplateResponse)
def read_prompt_template(
    *,
    db: Session = Depends(get_db),
    template_id: int
):
    """获取单个Prompt模板"""
    template = prompt_template.get(db=db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt模板不存在"
        )
    return template


@router.put("/{template_id}", response_model=PromptTemplateResponse)
def update_prompt_template(
    *,
    db: Session = Depends(get_db),
    template_id: int,
    template_in: PromptTemplateUpdate
):
    """更新Prompt模板"""
    template = prompt_template.get(db=db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt模板不存在"
        )
    
    try:
        template = prompt_template.update(
            db=db, db_obj=template, obj_in=template_in
        )
        return template
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新Prompt模板失败: {str(e)}"
        )


@router.delete("/{template_id}")
def delete_prompt_template(
    *,
    db: Session = Depends(get_db),
    template_id: int
):
    """删除Prompt模板"""
    template = prompt_template.get(db=db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt模板不存在"
        )
    
    prompt_template.remove(db=db, id=template_id)
    return {"message": "Prompt模板已删除"}


@router.post("/validate", response_model=PromptValidateResponse)
def validate_prompt(
    *,
    validate_request: PromptValidateRequest
):
    """验证Prompt内容"""
    try:
        result = prompt_service.validate_prompt(
            content=validate_request.content,
            variables=validate_request.variables
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证Prompt失败: {str(e)}"
        )


@router.post("/execute", response_model=PromptExecuteResponse)
async def execute_prompt(
    *,
    db: Session = Depends(get_db),
    execute_request: PromptExecuteRequest
):
    """执行Prompt（解析链式调用和变量）"""
    # 获取模板
    template = prompt_template.get(db=db, id=execute_request.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt模板不存在"
        )
    
    if not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt模板未激活"
        )
    
    try:
        start_time = time.time()
        
        # 解析Prompt内容
        resolved_content = await prompt_service.resolve_prompt_content(
            db=db,
            content=template.content,
            variables=execute_request.variables
        )
        
        execution_time = time.time() - start_time
        
        return PromptExecuteResponse(
            resolved_content=resolved_content,
            execution_time=execution_time,
            variables_used=execute_request.variables
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行Prompt失败: {str(e)}"
        )
