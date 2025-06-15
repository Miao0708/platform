"""
AI模型配置相关数据模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text, JSON
from app.models.base import BaseModel


class AIModelConfig(BaseModel, table=True):
    """AI模型配置模型"""
    
    __tablename__ = "ai_model_configs"
    
    name: str = Field(description="模型名称")
    provider: str = Field(description="提供商：openai, deepseek, local, etc.")
    base_url: str = Field(description="API基础URL")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    model: str = Field(description="模型名称")
    
    # 模型参数
    max_tokens: int = Field(default=4096, description="最大token数")
    temperature: float = Field(default=0.7, description="温度参数")
    top_p: Optional[float] = Field(default=None, description="Top-p参数")
    frequency_penalty: Optional[float] = Field(default=None, description="频率惩罚")
    presence_penalty: Optional[float] = Field(default=None, description="存在惩罚")
    
    # 状态和配置
    is_default: bool = Field(default=False, description="是否为默认模型")
    is_active: bool = Field(default=True, description="是否激活")
    timeout: int = Field(default=60, description="请求超时时间（秒）")
    
    # 统计信息
    usage_count: int = Field(default=0, description="使用次数")
    total_tokens_used: int = Field(default=0, description="总使用token数")
    last_used_at: Optional[str] = Field(default=None, description="最后使用时间")
    
    # 额外配置
    extra_config: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="额外配置参数")
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于AI服务调用"""
        return {
            "model_name": self.model,
            "provider": self.provider,
            "base_url": self.base_url,
            "api_key": self.api_key,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
            "extra_config": self.extra_config or {}
        }

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "OpenAI GPT-4o",
                    "provider": "openai",
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "sk-xxx",
                    "model": "gpt-4o",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "is_default": True,
                    "is_active": True,
                    "timeout": 60,
                    "extra_config": {
                        "supports_functions": True,
                        "supports_vision": True
                    }
                }
            ]
        }
    }


class AIModelTestResult(BaseModel, table=True):
    """AI模型测试结果模型"""
    
    __tablename__ = "ai_model_test_results"
    
    model_config_id: int = Field(foreign_key="ai_model_configs.id", description="模型配置ID")
    test_type: str = Field(description="测试类型：connection, performance, quality")
    
    # 测试结果
    success: bool = Field(description="是否成功")
    latency: Optional[float] = Field(default=None, description="延迟（毫秒）")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # 测试详情
    test_prompt: Optional[str] = Field(sa_column=Column(Text), default=None, description="测试提示")
    response_content: Optional[str] = Field(sa_column=Column(Text), default=None, description="响应内容")
    tokens_used: Optional[int] = Field(default=None, description="使用的token数")
    
    # 测试环境
    test_environment: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="测试环境信息")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model_config_id": 1,
                    "test_type": "connection",
                    "success": True,
                    "latency": 150.5,
                    "test_prompt": "Hello, this is a test.",
                    "response_content": "Hello! I'm working correctly.",
                    "tokens_used": 15,
                    "test_environment": {
                        "client_ip": "192.168.1.100",
                        "user_agent": "AI-Platform/1.0"
                    }
                }
            ]
        }
    }
