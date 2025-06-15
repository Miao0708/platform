"""
用户相关数据模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text, JSON
from app.models.base import BaseModel


class User(BaseModel, table=True):
    """用户模型"""
    
    __tablename__ = "users"
    
    username: str = Field(description="用户名", unique=True, index=True)
    email: str = Field(description="邮箱", unique=True, index=True)
    hashed_password: str = Field(description="加密后的密码")
    full_name: Optional[str] = Field(default=None, description="全名")
    avatar_url: Optional[str] = Field(default=None, description="头像URL")
    bio: Optional[str] = Field(sa_column=Column(Text), default=None, description="个人简介")
    
    # 个人设置
    preferences: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="个人偏好设置")
    
    # 状态字段
    is_active: bool = Field(default=True, description="是否激活")
    is_superuser: bool = Field(default=False, description="是否超级用户")
    is_verified: bool = Field(default=False, description="是否已验证邮箱")
    
    # 统计字段
    login_count: int = Field(default=0, description="登录次数")
    last_login_at: Optional[str] = Field(default=None, description="最后登录时间")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john_doe",
                    "email": "john@example.com",
                    "full_name": "John Doe",
                    "bio": "AI研发工程师",
                    "preferences": {
                        "theme": "dark",
                        "language": "zh-CN",
                        "notifications": {
                            "email": True,
                            "push": False
                        },
                        "editor": {
                            "font_size": 14,
                            "tab_size": 4,
                            "word_wrap": True
                        }
                    },
                    "is_active": True,
                    "is_verified": True
                }
            ]
        }
    }


class UserSession(BaseModel, table=True):
    """用户会话模型"""
    
    __tablename__ = "user_sessions"
    
    user_id: int = Field(foreign_key="users.id", description="用户ID")
    session_token: str = Field(description="会话令牌", unique=True, index=True)
    refresh_token: str = Field(description="刷新令牌", unique=True, index=True)
    expires_at: str = Field(description="过期时间")
    device_info: Optional[str] = Field(default=None, description="设备信息")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    is_active: bool = Field(default=True, description="是否激活")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 1,
                    "session_token": "sess_abc123...",
                    "refresh_token": "ref_xyz789...",
                    "expires_at": "2024-01-15T10:30:00Z",
                    "device_info": "Chrome 120.0 on Windows 10",
                    "ip_address": "192.168.1.100",
                    "is_active": True
                }
            ]
        }
    }


class UserLoginLog(BaseModel, table=True):
    """用户登录日志模型"""
    
    __tablename__ = "user_login_logs"
    
    user_id: int = Field(foreign_key="users.id", description="用户ID")
    login_type: str = Field(description="登录类型：password, token, oauth")
    ip_address: Optional[str] = Field(default=None, description="IP地址")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    device_info: Optional[str] = Field(default=None, description="设备信息")
    location: Optional[str] = Field(default=None, description="登录地点")
    success: bool = Field(description="是否成功")
    failure_reason: Optional[str] = Field(default=None, description="失败原因")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 1,
                    "login_type": "password",
                    "ip_address": "192.168.1.100",
                    "user_agent": "Mozilla/5.0...",
                    "device_info": "Chrome 120.0 on Windows 10",
                    "location": "北京市",
                    "success": True
                }
            ]
        }
    }
