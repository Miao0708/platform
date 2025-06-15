"""
Git配置相关数据模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.base import BaseModel


class GlobalGitCredential(BaseModel, table=True):
    """全局Git凭证模型"""
    
    __tablename__ = "global_git_credentials"
    
    username: str = Field(description="Git用户名")
    encrypted_token: str = Field(description="加密后的个人访问令牌")
    is_active: bool = Field(default=True, description="是否激活")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "your-username",
                    "encrypted_token": "encrypted_token_here",
                    "is_active": True
                }
            ]
        }
    }


class Repository(BaseModel, table=True):
    """仓库配置模型"""
    
    __tablename__ = "repositories"
    
    alias: str = Field(description="仓库别名", unique=True)
    url: str = Field(description="仓库URL")
    default_base_branch: Optional[str] = Field(
        default="main", description="默认基准分支"
    )
    description: Optional[str] = Field(default=None, description="仓库描述")
    is_active: bool = Field(default=True, description="是否激活")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "alias": "核心交易系统",
                    "url": "https://github.com/example/core-trading.git",
                    "default_base_branch": "main",
                    "description": "核心交易系统代码仓库",
                    "is_active": True
                }
            ]
        }
    }
