"""
统一响应格式处理
"""
from datetime import datetime
from typing import Any, Optional
from fastapi import Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel


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
    """标准JSON响应类"""
    
    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        message: str = "success",
        **kwargs
    ):
        response_data = StandardResponse(
            code=status_code,
            message=message,
            data=content
        )
        super().__init__(
            content=response_data.model_dump(),
            status_code=status_code,
            **kwargs
        )
