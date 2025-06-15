"""
Prompt模板相关数据模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text
from app.models.base import BaseModel


class PromptTemplate(BaseModel, table=True):
    """Prompt模板模型"""
    
    __tablename__ = "prompt_templates"
    
    name: str = Field(description="模板名称")
    identifier: str = Field(description="唯一标识符", unique=True, index=True)
    content: str = Field(sa_column=Column(Text), description="Prompt内容")
    description: Optional[str] = Field(default=None, description="模板说明")
    category: Optional[str] = Field(default=None, description="模板分类")
    is_active: bool = Field(default=True, description="是否激活")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "代码评审-安全漏洞扫描",
                    "identifier": "code_review_security",
                    "content": "你是一个代码安全专家，请分析以下代码差异中的安全漏洞：\n\n{{code_diff}}\n\n请重点关注：\n1. SQL注入\n2. XSS攻击\n3. 权限控制\n4. 数据验证",
                    "description": "专门用于检测代码中安全漏洞的Prompt模板",
                    "category": "code_review",
                    "is_active": True
                }
            ]
        }
    }
