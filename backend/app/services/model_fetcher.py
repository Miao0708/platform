"""
AI模型拉取服务
支持从不同AI服务商获取可用模型列表
"""
import httpx
import json
from typing import List, Dict, Any
from app.core.config import settings


async def fetch_models_from_provider(
    provider: str, 
    base_url: str, 
    api_key: str,
    timeout: int = 30
) -> List[Dict[str, Any]]:
    """从AI服务商获取模型列表"""
    
    models = []
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if provider == "openai":
                models = await _fetch_openai_models(client, base_url, headers)
            elif provider == "deepseek":
                models = await _fetch_deepseek_models(client, base_url, headers)
            elif provider == "gemini":
                models = await _fetch_gemini_models(client, base_url, headers)
            elif provider == "claude":
                models = await _fetch_claude_models(client, base_url, headers)
            elif provider == "spark":
                models = await _fetch_spark_models(client, base_url, headers)
            elif provider == "doubao":
                models = await _fetch_doubao_models(client, base_url, headers)
            else:
                # 尝试通用OpenAI格式
                models = await _fetch_openai_models(client, base_url, headers)
                
    except Exception as e:
        raise Exception(f"获取模型列表失败: {str(e)}")
    
    return models


async def _fetch_openai_models(
    client: httpx.AsyncClient, 
    base_url: str, 
    headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """获取OpenAI格式的模型列表"""
    url = f"{base_url.rstrip('/')}/v1/models"
    
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    models = []
    
    for model in data.get("data", []):
        models.append({
            "value": model["id"],
            "label": model["id"],
            "description": f"OpenAI模型: {model['id']}"
        })
    
    return models


async def _fetch_deepseek_models(
    client: httpx.AsyncClient, 
    base_url: str, 
    headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """获取DeepSeek模型列表"""
    # DeepSeek使用OpenAI兼容接口
    return await _fetch_openai_models(client, base_url, headers)


async def _fetch_gemini_models(
    client: httpx.AsyncClient, 
    base_url: str, 
    headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """获取Google Gemini模型列表"""
    # 返回常见的Gemini模型
    return [
        {"value": "gemini-pro", "label": "Gemini Pro", "description": "Google Gemini Pro模型"},
        {"value": "gemini-pro-vision", "label": "Gemini Pro Vision", "description": "支持图像的Gemini Pro模型"},
        {"value": "gemini-1.5-pro", "label": "Gemini 1.5 Pro", "description": "Gemini 1.5 Pro模型"}
    ]


async def _fetch_claude_models(
    client: httpx.AsyncClient, 
    base_url: str, 
    headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """获取Anthropic Claude模型列表"""
    # 返回常见的Claude模型
    return [
        {"value": "claude-3-opus-20240229", "label": "Claude 3 Opus", "description": "Claude 3 Opus模型"},
        {"value": "claude-3-sonnet-20240229", "label": "Claude 3 Sonnet", "description": "Claude 3 Sonnet模型"},
        {"value": "claude-3-haiku-20240307", "label": "Claude 3 Haiku", "description": "Claude 3 Haiku模型"}
    ]


async def _fetch_spark_models(
    client: httpx.AsyncClient, 
    base_url: str, 
    headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """获取讯飞星火模型列表"""
    # 返回常见的星火模型
    return [
        {"value": "spark-3.5", "label": "星火3.5", "description": "讯飞星火3.5模型"},
        {"value": "spark-3.0", "label": "星火3.0", "description": "讯飞星火3.0模型"},
        {"value": "spark-2.0", "label": "星火2.0", "description": "讯飞星火2.0模型"}
    ]


async def _fetch_doubao_models(
    client: httpx.AsyncClient, 
    base_url: str, 
    headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """获取字节豆包模型列表"""
    # 返回常见的豆包模型
    return [
        {"value": "doubao-pro-4k", "label": "豆包 Pro 4K", "description": "字节豆包Pro 4K模型"},
        {"value": "doubao-pro-32k", "label": "豆包 Pro 32K", "description": "字节豆包Pro 32K模型"},
        {"value": "doubao-lite-4k", "label": "豆包 Lite 4K", "description": "字节豆包Lite 4K模型"}
    ] 