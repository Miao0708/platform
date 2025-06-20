"""
AI Prompt模板管理API端点（适配前端需求）
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_prompt import prompt_template
from app.schemas.prompt import (
    PromptTemplateCreate, PromptTemplateUpdate, PromptTemplateResponse,
    PromptValidateRequest, PromptValidateResponse
)
from app.core.response import StandardJSONResponse
from app.services.prompt_service import prompt_service

router = APIRouter()


@router.get("/prompts", tags=["AI Prompt"])
def get_prompts(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取Prompt模板列表"""
    try:
        if category:
            prompts = prompt_template.get_by_category(db, category=category)
        else:
            prompts = prompt_template.get_multi(db, skip=skip, limit=limit)
        
        prompt_list = []
        for prompt in prompts:
            prompt_list.append({
                "id": str(prompt.id),
                "name": prompt.name,
                "identifier": prompt.identifier,
                "content": prompt.content,
                "description": prompt.description,
                "category": prompt.category,
                "variables": prompt.variables,
                "is_active": prompt.is_active,
                "usage_count": prompt.usage_count,
                "created_at": prompt.created_at.isoformat() + "Z" if prompt.created_at else None,
                "updated_at": prompt.updated_at.isoformat() + "Z" if prompt.updated_at else None
            })
        
        return StandardJSONResponse(
            content=prompt_list,
            message="获取Prompt模板列表成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取Prompt模板列表失败: {str(e)}"
        )


@router.post("/prompts", tags=["AI Prompt"])
def create_prompt(
    *,
    db: Session = Depends(get_db),
    prompt_in: PromptTemplateCreate
):
    """创建Prompt模板"""
    try:
        # 检查标识符是否已存在
        existing_prompt = prompt_template.get_by_identifier(db, identifier=prompt_in.identifier)
        if existing_prompt:
            return StandardJSONResponse(
                content=None,
                status_code=400,
                message=f"标识符 '{prompt_in.identifier}' 已存在"
            )
        
        prompt = prompt_template.create(db=db, obj_in=prompt_in)
        
        prompt_data = {
            "id": str(prompt.id),
            "name": prompt.name,
            "identifier": prompt.identifier,
            "content": prompt.content,
            "description": prompt.description,
            "category": prompt.category,
            "variables": prompt.variables,
            "is_active": prompt.is_active,
            "created_at": prompt.created_at.isoformat() + "Z"
        }
        
        return StandardJSONResponse(
            content=prompt_data,
            message="Prompt模板创建成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"创建Prompt模板失败: {str(e)}"
        )


@router.get("/prompts/{prompt_id}", tags=["AI Prompt"])
def get_prompt_detail(
    *,
    db: Session = Depends(get_db),
    prompt_id: str
):
    """获取Prompt模板详情"""
    try:
        prompt = prompt_template.get(db=db, id=int(prompt_id))
        if not prompt:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="Prompt模板不存在"
            )
        
        prompt_data = {
            "id": str(prompt.id),
            "name": prompt.name,
            "identifier": prompt.identifier,
            "content": prompt.content,
            "description": prompt.description,
            "category": prompt.category,
            "variables": prompt.variables,
            "is_active": prompt.is_active,
            "usage_count": prompt.usage_count,
            "created_at": prompt.created_at.isoformat() + "Z" if prompt.created_at else None,
            "updated_at": prompt.updated_at.isoformat() + "Z" if prompt.updated_at else None
        }
        
        return StandardJSONResponse(
            content=prompt_data,
            message="获取Prompt模板详情成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取Prompt模板详情失败: {str(e)}"
        )


@router.put("/prompts/{prompt_id}", tags=["AI Prompt"])
def update_prompt(
    *,
    db: Session = Depends(get_db),
    prompt_id: str,
    prompt_in: PromptTemplateUpdate
):
    """更新Prompt模板"""
    try:
        prompt = prompt_template.get(db=db, id=int(prompt_id))
        if not prompt:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="Prompt模板不存在"
            )
        
        # 如果更新标识符，检查是否冲突
        if prompt_in.identifier and prompt_in.identifier != prompt.identifier:
            existing_prompt = prompt_template.get_by_identifier(db, identifier=prompt_in.identifier)
            if existing_prompt:
                return StandardJSONResponse(
                    content=None,
                    status_code=400,
                    message=f"标识符 '{prompt_in.identifier}' 已存在"
                )
        
        updated_prompt = prompt_template.update(db=db, db_obj=prompt, obj_in=prompt_in)
        
        prompt_data = {
            "id": str(updated_prompt.id),
            "name": updated_prompt.name,
            "identifier": updated_prompt.identifier,
            "content": updated_prompt.content,
            "description": updated_prompt.description,
            "category": updated_prompt.category,
            "variables": updated_prompt.variables,
            "is_active": updated_prompt.is_active,
            "updated_at": updated_prompt.updated_at.isoformat() + "Z" if updated_prompt.updated_at else None
        }
        
        return StandardJSONResponse(
            content=prompt_data,
            message="Prompt模板更新成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"更新Prompt模板失败: {str(e)}"
        )


@router.delete("/prompts/{prompt_id}", tags=["AI Prompt"])
def delete_prompt(
    *,
    db: Session = Depends(get_db),
    prompt_id: str
):
    """删除Prompt模板"""
    try:
        prompt = prompt_template.get(db=db, id=int(prompt_id))
        if not prompt:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="Prompt模板不存在"
            )
        
        prompt_template.remove(db=db, id=int(prompt_id))
        
        return StandardJSONResponse(
            content=None,
            message="Prompt模板删除成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"删除Prompt模板失败: {str(e)}"
        )


@router.post("/prompts/validate", tags=["AI Prompt"])
async def validate_prompt(
    *,
    db: Session = Depends(get_db),
    validation_request: PromptValidateRequest
):
    """验证Prompt模板"""
    try:
        # 解析变量
        variables_found = prompt_service.extract_variables(validation_request.content)
        
        # 检查是否所有变量都有值
        missing_variables = []
        for var in variables_found:
            if var not in validation_request.variables:
                missing_variables.append(var)
        
        is_valid = len(missing_variables) == 0
        
        # 如果有效，尝试渲染
        rendered_content = None
        if is_valid:
            try:
                rendered_content = await prompt_service.resolve_prompt_content(
                    db, validation_request.content, validation_request.variables
                )
            except Exception as e:
                is_valid = False
                missing_variables = [f"渲染错误: {str(e)}"]
        
        validation_result = {
            "is_valid": is_valid,
            "variables_found": variables_found,
            "missing_variables": missing_variables,
            "rendered_content": rendered_content
        }
        
        return StandardJSONResponse(
            content=validation_result,
            message="Prompt验证完成"
        )
    except Exception as e:
        return StandardJSONResponse(
            content={
                "is_valid": False,
                "variables_found": [],
                "missing_variables": [f"验证错误: {str(e)}"],
                "rendered_content": None
            },
            status_code=500,
            message=f"Prompt验证失败: {str(e)}"
        )


@router.get("/prompts/categories", tags=["AI Prompt"])
def get_prompt_categories(db: Session = Depends(get_db)):
    """获取Prompt模板分类"""
    try:
        categories = prompt_template.get_categories(db)
        
        return StandardJSONResponse(
            content=categories,
            message="获取Prompt分类成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取Prompt分类失败: {str(e)}"
        )
