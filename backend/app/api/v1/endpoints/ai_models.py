"""
AI模型配置管理API端点（适配前端需求）
"""
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_ai_model import ai_model_config, ai_model_test_result
from app.schemas.ai_model import (
    AIModelConfigCreate, AIModelConfigUpdate, AIModelConfigResponse,
    AIModelTestRequest, AIModelTestResponse
)
from app.core.response import success_response, error_response, StandardJSONResponse
from app.core.llm_client import llm_manager

router = APIRouter()


@router.get("/models", tags=["AI模型"])
def get_ai_models(db: Session = Depends(get_db)):
    """获取AI模型列表"""
    try:
        models = ai_model_config.get_multi(db)
        model_list = []
        
        for model in models:
            model_data = {
                "id": str(model.id),
                "name": model.name,
                "provider": model.provider,
                "base_url": model.base_url,
                "model": model.model,
                "max_tokens": model.max_tokens,
                "temperature": model.temperature,
                "top_p": model.top_p,
                "frequency_penalty": model.frequency_penalty,
                "presence_penalty": model.presence_penalty,
                "is_default": model.is_default,
                "is_active": model.is_active,
                "timeout": model.timeout,
                "usage_count": model.usage_count,
                "total_tokens_used": model.total_tokens_used,
                "last_used_at": model.last_used_at,
                "extra_config": model.extra_config,
    
                "updated_at": model.updated_at
            }
            model_list.append(model_data)
        
        return StandardJSONResponse(
            content=model_list,
            message="获取AI模型列表成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取AI模型列表失败: {str(e)}"
        )


@router.post("/models", tags=["AI模型"])
def create_ai_model(
    *,
    db: Session = Depends(get_db),
    model_in: AIModelConfigCreate
):
    """创建AI模型配置"""
    try:
        # 如果设置为默认模型，先取消其他默认设置
        if model_in.is_default:
            ai_model_config.set_default_model(db, model_id=-1)  # 先清除所有默认
        
        model = ai_model_config.create(db=db, obj_in=model_in)
        
        # 如果是默认模型，设置为默认
        if model_in.is_default:
            ai_model_config.set_default_model(db, model_id=model.id)
        
        return StandardJSONResponse(
            content={
                "id": str(model.id),
                "name": model.name,
                "provider": model.provider,
                "model": model.model,
                "is_default": model.is_default,
                "is_active": model.is_active
            },
            message="AI模型配置创建成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"创建AI模型配置失败: {str(e)}"
        )


@router.get("/models/{model_id}", tags=["AI模型"])
def get_ai_model(
    *,
    db: Session = Depends(get_db),
    model_id: str
):
    """获取AI模型详情"""
    try:
        model = ai_model_config.get(db=db, id=int(model_id))
        if not model:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="AI模型配置不存在"
            )
        
        model_data = {
            "id": str(model.id),
            "name": model.name,
            "provider": model.provider,
            "base_url": model.base_url,
            "model": model.model,
            "max_tokens": model.max_tokens,
            "temperature": model.temperature,
            "top_p": model.top_p,
            "frequency_penalty": model.frequency_penalty,
            "presence_penalty": model.presence_penalty,
            "is_default": model.is_default,
            "is_active": model.is_active,
            "timeout": model.timeout,
            "usage_count": model.usage_count,
            "total_tokens_used": model.total_tokens_used,
            "last_used_at": model.last_used_at,
            "extra_config": model.extra_config,

        }
        
        return StandardJSONResponse(
            content=model_data,
            message="获取AI模型详情成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取AI模型详情失败: {str(e)}"
        )


@router.put("/models/{model_id}", tags=["AI模型"])
def update_ai_model(
    *,
    db: Session = Depends(get_db),
    model_id: str,
    model_in: AIModelConfigUpdate
):
    """更新AI模型配置"""
    try:
        model = ai_model_config.get(db=db, id=int(model_id))
        if not model:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="AI模型配置不存在"
            )
        
        # 如果设置为默认模型
        if model_in.is_default:
            ai_model_config.set_default_model(db, model_id=int(model_id))
        
        updated_model = ai_model_config.update(db=db, db_obj=model, obj_in=model_in)
        
        return StandardJSONResponse(
            content={
                "id": str(updated_model.id),
                "name": updated_model.name,
                "provider": updated_model.provider,
                "model": updated_model.model,
                "is_default": updated_model.is_default,
                "is_active": updated_model.is_active
            },
            message="AI模型配置更新成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"更新AI模型配置失败: {str(e)}"
        )


@router.delete("/models/{model_id}", tags=["AI模型"])
def delete_ai_model(
    *,
    db: Session = Depends(get_db),
    model_id: str
):
    """删除AI模型配置"""
    try:
        model = ai_model_config.get(db=db, id=int(model_id))
        if not model:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="AI模型配置不存在"
            )
        
        # 如果是默认模型，不允许删除
        if model.is_default:
            return StandardJSONResponse(
                content=None,
                status_code=400,
                message="不能删除默认模型配置"
            )
        
        ai_model_config.remove(db=db, id=int(model_id))
        
        return StandardJSONResponse(
            content=None,
            message="AI模型配置删除成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"删除AI模型配置失败: {str(e)}"
        )


@router.post("/models/{model_id}/test", tags=["AI模型"])
async def test_ai_model(
    *,
    db: Session = Depends(get_db),
    model_id: str,
    test_request: AIModelTestRequest
):
    """测试AI模型连接"""
    try:
        model = ai_model_config.get(db=db, id=int(model_id))
        if not model:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="AI模型配置不存在"
            )
        
        start_time = time.time()
        
        # 构建测试配置
        test_config = {
            "api_key": model.api_key,
            "base_url": model.base_url,
            "model": model.model,
            "temperature": model.temperature,
            "max_tokens": min(model.max_tokens, 100),  # 测试时限制token数
            "timeout": model.timeout
        }
        
        # 调用LLM进行测试
        llm_response = await llm_manager.text_completion(
            prompt=test_request.test_prompt,
            **test_config
        )
        
        latency = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 保存测试结果
        ai_model_test_result.create_test_result(
            db=db,
            model_config_id=int(model_id),
            test_type=test_request.test_type,
            success=llm_response.success,
            latency=latency,
            error_message=llm_response.error_message,
            test_prompt=test_request.test_prompt,
            response_content=llm_response.content if llm_response.success else None,
            tokens_used=llm_response.tokens_used,
            test_environment={"test_time": time.time()}
        )
        
        # 构建响应
        test_result = {
            "success": llm_response.success,
            "message": "连接测试成功" if llm_response.success else "连接测试失败",
            "latency": latency,
            "response_content": llm_response.content if llm_response.success else None,
            "tokens_used": llm_response.tokens_used,
            "error_details": llm_response.error_message if not llm_response.success else None
        }
        
        return StandardJSONResponse(
            content=test_result,
            message="AI模型测试完成"
        )
    except Exception as e:
        return StandardJSONResponse(
            content={
                "success": False,
                "message": "测试过程中发生错误",
                "error_details": str(e)
            },
            status_code=500,
            message=f"AI模型测试失败: {str(e)}"
        )


@router.post("/models/{model_id}/set-default", tags=["AI模型"])
def set_default_model(
    *,
    db: Session = Depends(get_db),
    model_id: str
):
    """设置默认AI模型"""
    try:
        success = ai_model_config.set_default_model(db, model_id=int(model_id))
        
        if success:
            return StandardJSONResponse(
                content=None,
                message="默认AI模型设置成功"
            )
        else:
            return StandardJSONResponse(
                content=None,
                status_code=404,
                message="AI模型配置不存在"
            )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"设置默认AI模型失败: {str(e)}"
        )


@router.post("/models/fetch", tags=["AI模型"])
async def fetch_available_models(
    *,
    db: Session = Depends(get_db),
    provider: str,
    base_url: str,
    api_key: str
):
    """从AI服务商获取可用模型列表"""
    try:
        from app.services.model_fetcher import fetch_models_from_provider
        
        models = await fetch_models_from_provider(
            provider=provider,
            base_url=base_url,
            api_key=api_key
        )
        
        return StandardJSONResponse(
            content=models,
            message=f"成功获取 {provider} 的模型列表"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=[],
            status_code=400,
            message=f"获取模型列表失败: {str(e)}"
        )
