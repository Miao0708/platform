"""
基础模型类
"""
from typing import Optional
from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    """基础模型类，包含通用字段"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    model_config = {"from_attributes": True}
