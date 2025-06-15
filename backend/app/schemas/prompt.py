"""
Prompt模板相关API数据模式
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PromptTemplateCreate(BaseModel):
    """创建Prompt模板的请求模式"""
    name: str = Field(..., description="模板名称")
    identifier: str = Field(..., description="唯一标识符")
    content: str = Field(..., description="Prompt内容")
    description: Optional[str] = Field(None, description="模板说明")
    category: Optional[str] = Field(None, description="模板分类")
    tags: Optional[list[str]] = Field(default_factory=list, description="标签列表")
    variables: Optional[list[str]] = Field(default_factory=list, description="变量列表")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "代码评审-安全漏洞扫描",
                    "identifier": "code_review_security",
                    "content": "你是一个代码安全专家，请分析以下代码差异中的安全漏洞：\n\n{{code_diff}}\n\n请重点关注：\n1. SQL注入\n2. XSS攻击\n3. 权限控制\n4. 数据验证",
                    "description": "专门用于检测代码中安全漏洞的Prompt模板",
                    "category": "code_review"
                }
            ]
        }
    }


class PromptTemplateUpdate(BaseModel):
    """更新Prompt模板的请求模式"""
    name: Optional[str] = Field(None, description="模板名称")
    identifier: Optional[str] = Field(None, description="唯一标识符")
    content: Optional[str] = Field(None, description="Prompt内容")
    description: Optional[str] = Field(None, description="模板说明")
    category: Optional[str] = Field(None, description="模板分类")
    tags: Optional[list[str]] = Field(None, description="标签列表")
    variables: Optional[list[str]] = Field(None, description="变量列表")
    is_active: Optional[bool] = Field(None, description="是否激活")


class PromptTemplateResponse(BaseModel):
    """Prompt模板响应模式"""
    id: int
    name: str
    identifier: str
    content: str
    description: Optional[str]
    category: Optional[str]
    tags: Optional[list[str]]
    variables: Optional[list[str]]
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class PromptExecuteRequest(BaseModel):
    """执行Prompt的请求模式"""
    template_id: int = Field(..., description="模板ID")
    variables: Dict[str, Any] = Field(default_factory=dict, description="变量字典")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "template_id": 1,
                    "variables": {
                        "code_diff": "diff --git a/file.py b/file.py\n...",
                        "requirement_text": "需要实现用户登录功能"
                    }
                }
            ]
        }
    }


class PromptExecuteResponse(BaseModel):
    """执行Prompt的响应模式"""
    resolved_content: str = Field(..., description="解析后的Prompt内容")
    execution_time: float = Field(..., description="执行时间（秒）")
    variables_used: Dict[str, Any] = Field(..., description="使用的变量")


class PromptValidateRequest(BaseModel):
    """验证Prompt的请求模式"""
    content: str = Field(..., description="Prompt内容")
    variables: Dict[str, Any] = Field(default_factory=dict, description="测试变量")


class PromptValidateResponse(BaseModel):
    """验证Prompt的响应模式"""
    is_valid: bool = Field(..., description="是否有效")
    errors: list[str] = Field(default_factory=list, description="错误信息")
    warnings: list[str] = Field(default_factory=list, description="警告信息")
    resolved_content: Optional[str] = Field(None, description="解析后的内容")
    variables_found: list[str] = Field(default_factory=list, description="发现的变量")
    chained_prompts: list[str] = Field(default_factory=list, description="链式调用的Prompt")
