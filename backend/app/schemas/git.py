"""
Git配置相关API数据模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GitCredentialCreate(BaseModel):
    """创建Git凭证的请求模式"""
    username: str = Field(..., description="Git用户名")
    token: str = Field(..., description="个人访问令牌")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "your-username",
                    "token": "ghp_xxxxxxxxxxxxxxxxxxxx"
                }
            ]
        }
    }


class GitCredentialUpdate(BaseModel):
    """更新Git凭证的请求模式"""
    username: Optional[str] = Field(None, description="Git用户名")
    token: Optional[str] = Field(None, description="个人访问令牌")
    is_active: Optional[bool] = Field(None, description="是否激活")


class GitCredentialResponse(BaseModel):
    """Git凭证响应模式"""
    id: int
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class GitConnectionTestRequest(BaseModel):
    """Git连接测试请求模式"""
    test_url: Optional[str] = Field(None, description="测试URL，不提供则使用默认仓库")


class GitConnectionTestResponse(BaseModel):
    """Git连接测试响应模式"""
    success: bool
    message: str
    test_url: Optional[str] = None


class RepositoryCreate(BaseModel):
    """创建仓库配置的请求模式"""
    alias: str = Field(..., description="仓库别名")
    url: str = Field(..., description="仓库URL")
    default_base_branch: Optional[str] = Field("main", description="默认基准分支")
    description: Optional[str] = Field(None, description="仓库描述")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "alias": "核心交易系统",
                    "url": "https://github.com/example/core-trading.git",
                    "default_base_branch": "main",
                    "description": "核心交易系统代码仓库"
                }
            ]
        }
    }


class RepositoryUpdate(BaseModel):
    """更新仓库配置的请求模式"""
    alias: Optional[str] = Field(None, description="仓库别名")
    url: Optional[str] = Field(None, description="仓库URL")
    default_base_branch: Optional[str] = Field(None, description="默认基准分支")
    description: Optional[str] = Field(None, description="仓库描述")
    is_active: Optional[bool] = Field(None, description="是否激活")


class RepositoryResponse(BaseModel):
    """仓库配置响应模式"""
    id: int
    alias: str
    url: str
    default_base_branch: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class BranchInfo(BaseModel):
    """分支信息模式"""
    name: str
    commit_hash: str
    commit_message: str


class CommitInfo(BaseModel):
    """提交信息模式"""
    hash: str
    author: str
    message: str
    date: str
