"""
AI对话相关数据模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text, JSON
from app.models.base import BaseModel


class Conversation(BaseModel, table=True):
    """对话模型"""
    
    __tablename__ = "conversations"
    
    user_id: int = Field(foreign_key="users.id", description="用户ID")
    title: str = Field(description="对话标题")
    model_config_id: int = Field(foreign_key="ai_model_configs.id", description="AI模型配置ID")
    
    # 统计信息
    total_tokens: int = Field(default=0, description="总使用token数")
    message_count: int = Field(default=0, description="消息数量")
    last_message_at: Optional[str] = Field(default=None, description="最后消息时间")
    
    # 对话配置
    system_prompt: Optional[str] = Field(sa_column=Column(Text), default=None, description="系统提示")
    context_config: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="上下文配置")
    
    # 状态
    is_active: bool = Field(default=True, description="是否激活")
    is_pinned: bool = Field(default=False, description="是否置顶")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 1,
                    "title": "代码评审讨论",
                    "model_config_id": 1,
                    "total_tokens": 1500,
                    "message_count": 8,
                    "last_message_at": "2024-01-01T10:30:00Z",
                    "system_prompt": "你是一个专业的代码评审专家",
                    "is_active": True,
                    "is_pinned": False
                }
            ]
        }
    }


class Message(BaseModel, table=True):
    """消息模型"""
    
    __tablename__ = "messages"
    
    conversation_id: int = Field(foreign_key="conversations.id", description="对话ID")
    role: str = Field(description="角色：user, assistant, system")
    content: str = Field(sa_column=Column(Text), description="消息内容")
    
    # 消息元数据
    tokens: Optional[int] = Field(default=None, description="token数量")
    model_used: Optional[str] = Field(default=None, description="使用的模型")
    prompt_template_id: Optional[int] = Field(default=None, foreign_key="prompt_templates.id", description="使用的Prompt模板ID")
    
    # 处理信息
    processing_time: Optional[float] = Field(default=None, description="处理时间（秒）")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # 上下文信息
    context_data: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="上下文数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "conversation_id": 1,
                    "role": "user",
                    "content": "请帮我分析这段代码的安全性",
                    "tokens": 15,
                    "context_data": {
                        "code_snippet": "function login(username, password) {...}",
                        "file_path": "auth.js"
                    }
                }
            ]
        }
    }
