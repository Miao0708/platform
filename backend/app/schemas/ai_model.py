"""
AI模型配置相关API数据模式
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ===== AI模型配置相关 =====
class AIModelConfigCreate(BaseModel):
    """创建AI模型配置的请求模式"""
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商")
    base_url: str = Field(..., description="API基础URL")
    api_key: Optional[str] = Field(None, description="API密钥")
    model: str = Field(..., description="模型名称")
    max_tokens: int = Field(4096, description="最大token数")
    temperature: float = Field(0.7, description="温度参数")
    top_p: Optional[float] = Field(None, description="Top-p参数")
    frequency_penalty: Optional[float] = Field(None, description="频率惩罚")
    presence_penalty: Optional[float] = Field(None, description="存在惩罚")
    is_default: bool = Field(False, description="是否为默认模型")
    is_active: bool = Field(True, description="是否激活")
    timeout: int = Field(60, description="请求超时时间")
    extra_config: Optional[Dict[str, Any]] = Field(None, description="额外配置参数")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "DeepSeek Chat",
                    "provider": "deepseek",
                    "base_url": "https://api.deepseek.com/v1",
                    "api_key": "sk-xxx",
                    "model": "deepseek-chat",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "is_default": False,
                    "is_active": True
                }
            ]
        }
    }


class AIModelConfigUpdate(BaseModel):
    """更新AI模型配置的请求模式"""
    name: Optional[str] = Field(None, description="模型名称")
    provider: Optional[str] = Field(None, description="提供商")
    base_url: Optional[str] = Field(None, description="API基础URL")
    api_key: Optional[str] = Field(None, description="API密钥")
    model: Optional[str] = Field(None, description="模型名称")
    max_tokens: Optional[int] = Field(None, description="最大token数")
    temperature: Optional[float] = Field(None, description="温度参数")
    top_p: Optional[float] = Field(None, description="Top-p参数")
    frequency_penalty: Optional[float] = Field(None, description="频率惩罚")
    presence_penalty: Optional[float] = Field(None, description="存在惩罚")
    is_default: Optional[bool] = Field(None, description="是否为默认模型")
    is_active: Optional[bool] = Field(None, description="是否激活")
    timeout: Optional[int] = Field(None, description="请求超时时间")
    extra_config: Optional[Dict[str, Any]] = Field(None, description="额外配置参数")


class AIModelConfigResponse(BaseModel):
    """AI模型配置响应模式"""
    id: str
    name: str
    provider: str
    base_url: str
    model: str
    max_tokens: int
    temperature: float
    top_p: Optional[float]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]
    is_default: bool
    is_active: bool
    timeout: int
    usage_count: int
    total_tokens_used: int
    last_used_at: Optional[str]
    extra_config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class AIModelTestRequest(BaseModel):
    """AI模型测试请求模式"""
    test_prompt: Optional[str] = Field("Hello, this is a connection test.", description="测试提示")
    test_type: str = Field("connection", description="测试类型")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "test_prompt": "请回复'测试成功'",
                    "test_type": "connection"
                }
            ]
        }
    }


class AIModelTestResponse(BaseModel):
    """AI模型测试响应模式"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="测试消息")
    latency: Optional[float] = Field(None, description="延迟（毫秒）")
    response_content: Optional[str] = Field(None, description="响应内容")
    tokens_used: Optional[int] = Field(None, description="使用的token数")
    error_details: Optional[str] = Field(None, description="错误详情")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "连接测试成功",
                    "latency": 150,
                    "response_content": "测试成功",
                    "tokens_used": 10
                }
            ]
        }
    }


# ===== AI对话相关 =====
class ConversationCreate(BaseModel):
    """创建对话的请求模式"""
    title: str = Field(..., description="对话标题")
    model_config_id: str = Field(..., description="AI模型配置ID")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "新的对话",
                    "model_config_id": "1"
                }
            ]
        }
    }


class ConversationUpdate(BaseModel):
    """更新对话的请求模式"""
    title: Optional[str] = Field(None, description="对话标题")


class MessageCreate(BaseModel):
    """创建消息的请求模式"""
    content: str = Field(..., description="消息内容")
    model_config_id: Optional[str] = Field(None, description="AI模型配置ID")
    prompt_template_id: Optional[str] = Field(None, description="Prompt模板ID")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文变量")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "请帮我分析这个需求",
                    "model_config_id": "1",
                    "prompt_template_id": "2",
                    "context": {
                        "requirement": "用户登录功能",
                        "code_diff": "diff内容"
                    }
                }
            ]
        }
    }


class MessageResponse(BaseModel):
    """消息响应模式"""
    id: str
    role: str  # user, assistant
    content: str
    timestamp: str
    tokens: Optional[int]
    
    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """对话响应模式"""
    id: str
    title: str
    model_config_id: str
    total_tokens: int
    message_count: int
    last_message_at: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ConversationDetailResponse(BaseModel):
    """对话详情响应模式"""
    id: str
    title: str
    model_config_id: str
    messages: list[MessageResponse]
    total_tokens: int
    
    model_config = {"from_attributes": True}


# ===== 仪表盘统计相关 =====
class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_tasks: int = Field(description="总任务数")
    completed_tasks: int = Field(description="已完成任务数")
    running_tasks: int = Field(description="运行中任务数")
    failed_tasks: int = Field(description="失败任务数")
    total_tokens_used: int = Field(description="总使用token数")
    recent_tasks: list[Dict[str, Any]] = Field(description="最近任务")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_tasks": 156,
                    "completed_tasks": 142,
                    "running_tasks": 8,
                    "failed_tasks": 6,
                    "total_tokens_used": 125000,
                    "recent_tasks": [
                        {
                            "id": "1",
                            "name": "代码评审任务",
                            "type": "code_review",
                            "status": "completed",
                            "created_at": "2024-01-01T10:00:00Z"
                        }
                    ]
                }
            ]
        }
    }
