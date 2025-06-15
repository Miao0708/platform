"""
用户相关API数据模式
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


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
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    
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


class UserLoginResponse(BaseModel):
    """用户登录响应模式"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: "UserResponse" = Field(..., description="用户信息")


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


class PasswordChange(BaseModel):
    """密码修改请求模式"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")


# ===== 通用响应 =====
class MessageResponse(BaseModel):
    """通用消息响应模式"""
    message: str = Field(..., description="响应消息")
    success: bool = Field(default=True, description="是否成功")
