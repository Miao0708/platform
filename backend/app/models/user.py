"""
用户相关数据模型
"""
from sqlmodel import SQLModel, Field
from app.models.base import BaseModel


class User(BaseModel, table=True):
    """用户模型"""
    
    __tablename__ = "users"
    
    username: str = Field(description="用户名", unique=True, index=True)
    hashed_password: str = Field(description="加密后的密码")
    
    # 权限字段
    is_active: bool = Field(default=True, description="是否激活")
    is_superuser: bool = Field(default=False, description="是否超级用户")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "is_active": True,
                    "is_superuser": True
                }
            ]
        }
    }
