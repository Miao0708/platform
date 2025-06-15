"""
用户相关API数据模式
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# ===== 用户注册和登录 =====
class UserRegister(BaseModel):
    """用户注册请求模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "password": "admin123456"
                }
            ]
        }
    }


class UserLogin(BaseModel):
    """用户登录请求模式"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我")
    # device_info: Optional[str] = Field(None, description="设备信息")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john_doe",
                    "password": "secure_password123",
                    "remember_me": True,
                    # "device_info": "Chrome 120.0 on Windows 10"
                }
            ]
        }
    }


class UserLoginResponse(BaseModel):
    """用户登录响应模式"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: "UserResponse" = Field(..., description="用户信息")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh_token": "ref_xyz789...",
                    "token_type": "bearer",
                    "expires_in": 1800,
                    "user": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "full_name": "John Doe"
                    }
                }
            ]
        }
    }


# ===== 用户信息 =====
class UserResponse(BaseModel):
    """用户信息响应模式"""
    id: int
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """用户信息更新请求模式"""
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_superuser: Optional[bool] = Field(None, description="是否超级用户")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "is_active": True,
                    "is_superuser": False
                }
            ]
        }
    }


class UserPreferencesUpdate(BaseModel):
    """用户偏好设置更新请求模式"""
    theme: Optional[str] = Field(None, description="主题：light, dark, auto")
    language: Optional[str] = Field(None, description="语言：zh-CN, en-US")
    notifications: Optional[Dict[str, bool]] = Field(None, description="通知设置")
    editor: Optional[Dict[str, Any]] = Field(None, description="编辑器设置")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "theme": "dark",
                    "language": "zh-CN",
                    "notifications": {
                        "email": True,
                        "push": False,
                        "task_completion": True,
                        "system_updates": False
                    },
                    "editor": {
                        "font_size": 14,
                        "tab_size": 4,
                        "word_wrap": True,
                        "line_numbers": True,
                        "auto_save": True
                    }
                }
            ]
        }
    }


class PasswordChange(BaseModel):
    """密码修改请求模式"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_password": "old_password123",
                    "new_password": "new_secure_password456",
                    "confirm_password": "new_secure_password456"
                }
            ]
        }
    }


# ===== 会话管理 =====
class UserSessionResponse(BaseModel):
    """用户会话响应模式"""
    id: int
    session_token: str
    device_info: Optional[str]
    ip_address: Optional[str]
    expires_at: str
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模式"""
    refresh_token: str = Field(..., description="刷新令牌")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "ref_xyz789..."
                }
            ]
        }
    }


# ===== 登录日志 =====
class UserLoginLogResponse(BaseModel):
    """用户登录日志响应模式"""
    id: int
    login_type: str
    ip_address: Optional[str]
    device_info: Optional[str]
    location: Optional[str]
    success: bool
    failure_reason: Optional[str]
    created_at: datetime
    
    model_config = {"from_attributes": True}


# ===== 用户统计 =====
class UserStats(BaseModel):
    """用户统计信息"""
    total_users: int = Field(description="总用户数")
    active_users: int = Field(description="活跃用户数")
    verified_users: int = Field(description="已验证用户数")
    new_users_today: int = Field(description="今日新增用户")
    login_sessions: int = Field(description="当前登录会话数")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_users": 1250,
                    "active_users": 890,
                    "verified_users": 1100,
                    "new_users_today": 15,
                    "login_sessions": 234
                }
            ]
        }
    }


# ===== 通用响应 =====
class MessageResponse(BaseModel):
    """通用消息响应模式"""
    message: str = Field(..., description="响应消息")
    success: bool = Field(default=True, description="是否成功")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "操作成功",
                    "success": True
                }
            ]
        }
    }
