"""
统一响应格式处理
"""
import re
from datetime import datetime
from typing import Any, Optional, Dict, Union
from fastapi import Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel


def to_camel_case(snake_str: str) -> str:
    """将snake_case转换为camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def convert_keys_to_camel_case(data: Any) -> Any:
    """递归地将字典中的所有键从snake_case转换为camelCase"""
    if isinstance(data, dict):
        return {
            to_camel_case(key) if isinstance(key, str) else key: convert_keys_to_camel_case(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [convert_keys_to_camel_case(item) for item in data]
    elif hasattr(data, '__dict__'):
        # 处理Pydantic模型和其他对象
        if hasattr(data, 'model_dump'):
            # Pydantic v2模型
            return convert_keys_to_camel_case(data.model_dump())
        elif hasattr(data, 'dict'):
            # Pydantic v1模型
            return convert_keys_to_camel_case(data.dict())
        else:
            # 普通对象
            return convert_keys_to_camel_case(data.__dict__)
    else:
        return data


def to_snake_case(camel_str: str) -> str:
    """将camelCase转换为snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def convert_keys_to_snake_case(data: Any) -> Any:
    """递归地将字典中的所有键从camelCase转换为snake_case"""
    if isinstance(data, dict):
        return {
            to_snake_case(key) if isinstance(key, str) else key: convert_keys_to_snake_case(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data]
    else:
        return data


class StandardResponse(BaseModel):
    """标准响应格式"""
    code: int = 200
    message: str = "success"
    data: Any = None
    timestamp: str = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat() + "Z"
        super().__init__(**data)


def success_response(
    data: Any = None, 
    message: str = "success", 
    code: int = 200
) -> StandardResponse:
    """成功响应"""
    return StandardResponse(
        code=code,
        message=message,
        data=data
    )


def error_response(
    message: str = "error", 
    code: int = 400,
    data: Any = None
) -> StandardResponse:
    """错误响应"""
    return StandardResponse(
        code=code,
        message=message,
        data=data
    )


class StandardJSONResponse(JSONResponse):
    """标准JSON响应类，支持camelCase转换"""
    
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        message: str = "success",
        camel_case: bool = True,
        **kwargs
    ):
        response_data = StandardResponse(
            code=status_code,
            message=message,
            data=content
        )
        
        # 转换为字典
        response_dict = response_data.model_dump()
        
        # 如果启用camelCase转换，则转换所有键名
        if camel_case:
            response_dict = convert_keys_to_camel_case(response_dict)
        
        super().__init__(
            content=response_dict,
            status_code=status_code,
            **kwargs
        )


class CamelCaseJSONResponse(StandardJSONResponse):
    """强制使用camelCase的JSON响应类"""
    
    def __init__(self, *args, **kwargs):
        kwargs['camel_case'] = True
        super().__init__(*args, **kwargs)


class SnakeCaseJSONResponse(StandardJSONResponse):
    """保持snake_case的JSON响应类（用于特殊情况）"""
    
    def __init__(self, *args, **kwargs):
        kwargs['camel_case'] = False
        super().__init__(*args, **kwargs)


# ===== 便捷的响应函数 =====
def success_json_response(
    data: Any = None,
    message: str = "success",
    status_code: int = 200,
    camel_case: bool = True
) -> StandardJSONResponse:
    """成功响应（JSON格式）"""
    return StandardJSONResponse(
        content=data,
        status_code=status_code,
        message=message,
        camel_case=camel_case
    )


def error_json_response(
    message: str = "error",
    status_code: int = 400,
    data: Any = None,
    camel_case: bool = True
) -> StandardJSONResponse:
    """错误响应（JSON格式）"""
    return StandardJSONResponse(
        content=data,
        status_code=status_code,
        message=message,
        camel_case=camel_case
    )
