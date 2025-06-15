"""
Git配置相关API数据模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GitPlatformConfigCreate(BaseModel):
    """创建Git平台配置的请求模式"""
    name: str = Field(..., description="平台配置名称")
    platform: str = Field(..., description="平台类型（github, gitlab, gitee, coding, custom）")
    username: str = Field(..., description="Git用户名")
    token: str = Field(..., description="个人访问令牌")
    base_url: Optional[str] = Field(None, description="自定义平台基础URL")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "公司GitHub",
                    "platform": "github",
                    "username": "your-username",
                    "token": "ghp_xxxxxxxxxxxxxxxxxxxx",
                    "base_url": None
                }
            ]
        }
    }


class GitPlatformConfigUpdate(BaseModel):
    """更新Git平台配置的请求模式"""
    name: Optional[str] = Field(None, description="平台配置名称")
    platform: Optional[str] = Field(None, description="平台类型")
    username: Optional[str] = Field(None, description="Git用户名")
    token: Optional[str] = Field(None, description="个人访问令牌")
    base_url: Optional[str] = Field(None, description="自定义平台基础URL")
    is_active: Optional[bool] = Field(None, description="是否激活")


class GitPlatformConfigResponse(BaseModel):
    """Git平台配置响应模式"""
    id: int
    name: str
    platform: str
    username: str
    base_url: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class GitPlatformTestRequest(BaseModel):
    """Git平台连接测试请求模式"""
    platform_config_id: Optional[int] = Field(None, description="平台配置ID")
    test_url: Optional[str] = Field(None, description="测试URL")


class GitPlatformTestResponse(BaseModel):
    """Git平台连接测试响应模式"""
    success: bool
    message: str
    test_url: Optional[str] = None


class GitCredentialCreate(BaseModel):
    """创建Git凭证的请求模式（兼容性保留）"""
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
    """更新Git凭证的请求模式（兼容性保留）"""
    username: Optional[str] = Field(None, description="Git用户名")
    token: Optional[str] = Field(None, description="个人访问令牌")
    is_active: Optional[bool] = Field(None, description="是否激活")


class GitCredentialResponse(BaseModel):
    """Git凭证响应模式（兼容性保留）"""
    id: int
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class GitConnectionTestRequest(BaseModel):
    """Git连接测试请求模式（兼容性保留）"""
    test_url: Optional[str] = Field(None, description="测试URL，不提供则使用默认仓库")


class GitConnectionTestResponse(BaseModel):
    """Git连接测试响应模式（兼容性保留）"""
    success: bool
    message: str
    test_url: Optional[str] = None


class RepositoryCreate(BaseModel):
    """创建仓库配置的请求模式"""
    alias: str = Field(..., description="仓库别名")
    url: str = Field(..., description="仓库URL")
    platform_config_id: int = Field(..., description="关联的Git平台配置ID")
    default_base_branch: Optional[str] = Field("main", description="默认基准分支")
    description: Optional[str] = Field(None, description="仓库描述")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "alias": "核心交易系统",
                    "url": "https://github.com/example/core-trading.git",
                    "platform_config_id": 1,
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
    platform_config_id: Optional[int] = Field(None, description="关联的Git平台配置ID")
    default_base_branch: Optional[str] = Field(None, description="默认基准分支")
    description: Optional[str] = Field(None, description="仓库描述")
    is_active: Optional[bool] = Field(None, description="是否激活")


class RepositoryResponse(BaseModel):
    """仓库配置响应模式"""
    id: int
    alias: str
    url: str
    platform_config_id: Optional[int]
    default_base_branch: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # 关联的平台配置信息（用于前端显示）
    platform_name: Optional[str] = None
    
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
