"""
流水线相关数据模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text, JSON
from app.models.base import BaseModel


class CodeDiff(BaseModel, table=True):
    """代码差异模型"""
    
    __tablename__ = "code_diffs"
    
    repository_id: int = Field(foreign_key="repositories.id", description="仓库ID")
    base_ref: str = Field(description="基准分支/提交")
    head_ref: str = Field(description="目标分支/提交")
    diff_file_path: Optional[str] = Field(default=None, description="差异文件存储路径")
    status: str = Field(default="pending", description="状态：pending, generating, completed, failed")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    diff_metadata: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "repository_id": 1,
                    "base_ref": "main",
                    "head_ref": "feature/new-api",
                    "diff_file_path": "/diffs/repo1_main_feature_new_api.diff",
                    "status": "completed",
                    "diff_metadata": {
                        "files_changed": 5,
                        "lines_added": 120,
                        "lines_deleted": 30
                    }
                }
            ]
        }
    }


class RequirementText(BaseModel, table=True):
    """需求文本模型"""
    
    __tablename__ = "requirement_texts"
    
    title: str = Field(description="需求标题")
    original_content: str = Field(sa_column=Column(Text), description="原始需求内容")
    refined_content: Optional[str] = Field(sa_column=Column(Text), default=None, description="精炼后的需求内容")
    category: Optional[str] = Field(default=None, description="需求分类")
    priority: str = Field(default="medium", description="优先级：low, medium, high, urgent")
    status: str = Field(default="draft", description="状态：draft, reviewed, approved")
    req_metadata: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "用户登录功能优化",
                    "original_content": "需要优化用户登录功能，提高安全性和用户体验...",
                    "refined_content": "1. 添加双因子认证\n2. 优化登录界面\n3. 增加密码强度检查",
                    "category": "security",
                    "priority": "high",
                    "status": "approved",
                    "req_metadata": {
                        "estimated_hours": 40,
                        "assigned_team": "backend"
                    }
                }
            ]
        }
    }



