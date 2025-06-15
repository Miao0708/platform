"""
Git配置相关数据模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.base import BaseModel


class GitPlatformConfig(BaseModel, table=True):
    """Git平台配置模型"""
    
    __tablename__ = "git_platform_configs"
    
    name: str = Field(description="平台配置名称", index=True)
    platform: str = Field(description="平台类型（github, gitlab, gitee, coding, custom）")
    username: str = Field(description="Git用户名")
    encrypted_token: str = Field(description="加密后的个人访问令牌")
    base_url: Optional[str] = Field(default=None, description="自定义平台基础URL")
    is_active: bool = Field(default=True, description="是否激活")
    
    # 关联的仓库
    repositories: list["Repository"] = Relationship(back_populates="platform_config")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "公司GitHub",
                    "platform": "github",
                    "username": "your-username",
                    "encrypted_token": "encrypted_token_here",
                    "base_url": None,
                    "is_active": True
                }
            ]
        }
    }


class GlobalGitCredential(BaseModel, table=True):
    """全局Git凭证模型（兼容性保留）"""
    
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
    
    alias: str = Field(description="仓库别名", index=True)
    url: str = Field(description="仓库URL")
    default_base_branch: Optional[str] = Field(
        default="main", description="默认基准分支"
    )
    description: Optional[str] = Field(default=None, description="仓库描述")
    is_active: bool = Field(default=True, description="是否激活")
    
    # 关联的Git平台配置
    platform_config_id: Optional[int] = Field(
        default=None, foreign_key="git_platform_configs.id", description="关联的Git平台配置ID"
    )
    platform_config: Optional[GitPlatformConfig] = Relationship(back_populates="repositories")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "alias": "核心交易系统",
                    "url": "https://github.com/example/core-trading.git",
                    "default_base_branch": "main",
                    "description": "核心交易系统代码仓库",
                    "is_active": True,
                    "platform_config_id": 1
                }
            ]
        }
    }
