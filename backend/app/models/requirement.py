"""
需求文档相关数据模型
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text, JSON
from app.models.base import BaseModel


class RequirementDocument(BaseModel, table=True):
    """需求文档模型"""
    
    __tablename__ = "requirement_documents"
    
    name: str = Field(description="需求名称")
    original_content: str = Field(sa_column=Column(Text), description="原始需求内容")
    optimized_content: Optional[str] = Field(sa_column=Column(Text), default=None, description="优化后的需求内容")
    source: str = Field(description="来源：upload, manual")
    original_filename: Optional[str] = Field(default=None, description="原始文件名")
    file_type: Optional[str] = Field(default=None, description="文件类型：pdf, md, txt, docx")
    status: str = Field(default="pending", description="状态：pending, processing, completed, failed")
    
    # AI分析相关字段
    prompt_template_id: Optional[int] = Field(default=None, description="Prompt模板ID")
    model_config_id: Optional[int] = Field(default=None, description="AI模型配置ID")
    parse_task_id: Optional[str] = Field(default=None, description="解析任务ID")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # 时间戳
    task_started_at: Optional[str] = Field(default=None, description="任务开始时间")
    task_completed_at: Optional[str] = Field(default=None, description="任务完成时间")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "用户登录功能需求",
                    "original_content": "系统需要实现用户登录功能，支持用户名密码登录",
                    "source": "manual",
                    "status": "pending"
                }
            ]
        }
    }


class RequirementAnalysisTask(BaseModel, table=True):
    """需求分析任务模型"""
    
    __tablename__ = "requirement_analysis_tasks"
    
    requirement_document_id: int = Field(description="需求文档ID")
    prompt_template_id: int = Field(description="Prompt模板ID")
    model_config_id: int = Field(description="AI模型配置ID")
    status: str = Field(default="pending", description="任务状态")
    
    # 执行结果
    result: Optional[str] = Field(sa_column=Column(Text), default=None, description="分析结果")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    tokens_used: Optional[int] = Field(default=None, description="使用的tokens数量")
    execution_time: Optional[float] = Field(default=None, description="执行时间（秒）")
    
    # 时间戳
    started_at: Optional[str] = Field(default=None, description="开始时间")
    completed_at: Optional[str] = Field(default=None, description="完成时间")


class RequirementTestTask(BaseModel, table=True):
    """需求测试分析任务模型"""
    
    __tablename__ = "requirement_test_tasks"
    
    name: str = Field(description="任务名称")
    requirement_id: Optional[int] = Field(default=None, description="关联的需求文档ID")
    requirement_content: Optional[str] = Field(sa_column=Column(Text), default=None, description="直接输入的需求内容")
    prompt_template_id: int = Field(description="Prompt模板ID")
    model_config_id: int = Field(description="AI模型配置ID")
    status: str = Field(default="pending", description="任务状态")
    
    # 执行结果
    result: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="测试分析结果")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    tokens_used: Optional[int] = Field(default=None, description="使用的tokens数量")
    execution_time: Optional[float] = Field(default=None, description="执行时间（秒）")
    
    # 时间戳
    started_at: Optional[str] = Field(default=None, description="开始时间")
    completed_at: Optional[str] = Field(default=None, description="完成时间")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "用户登录功能测试分析",
                    "requirement_content": "用户可以通过用户名密码登录系统",
                    "prompt_template_id": 1,
                    "model_config_id": 1,
                    "status": "pending"
                }
            ]
        }
    } 