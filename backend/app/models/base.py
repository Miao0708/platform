"""
基础模型类
"""
from datetime import datetime,UTC
from typing import Optional
from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    """基础模型类，包含通用字段"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    # created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = Field(default=None)
    model_config = {"from_attributes": True}
