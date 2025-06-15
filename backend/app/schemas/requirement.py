"""
需求文档相关API数据模式
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


# ===== 需求文档相关 =====
class RequirementDocumentCreate(BaseModel):
    """创建需求文档的请求模式"""
    name: str = Field(..., description="需求名称")
    original_content: str = Field(..., description="原始需求内容") 
    source: str = Field(..., description="来源：upload, manual")
    original_filename: Optional[str] = Field(None, description="原始文件名")
    file_type: Optional[str] = Field(None, description="文件类型")
    prompt_template_id: Optional[int] = Field(None, description="Prompt模板ID")
    model_config_id: Optional[int] = Field(None, description="AI模型配置ID")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "用户登录功能需求",
                    "original_content": "系统需要实现用户登录功能，支持用户名密码登录...",
                    "source": "manual",
                    "prompt_template_id": 1,
                    "model_config_id": 1
                }
            ]
        }
    }


class RequirementDocumentUpdate(BaseModel):
    """更新需求文档的请求模式"""
    name: Optional[str] = Field(None, description="需求名称")
    original_content: Optional[str] = Field(None, description="原始需求内容")
    optimized_content: Optional[str] = Field(None, description="优化后的需求内容")
    prompt_template_id: Optional[int] = Field(None, description="Prompt模板ID")
    model_config_id: Optional[int] = Field(None, description="AI模型配置ID")
    status: Optional[str] = Field(None, description="状态")


class RequirementDocumentResponse(BaseModel):
    """需求文档响应模式"""
    id: int
    name: str
    original_content: str
    optimized_content: Optional[str]
    source: str
    original_filename: Optional[str]
    file_type: Optional[str]
    status: str
    prompt_template_id: Optional[int]
    model_config_id: Optional[int]
    parse_task_id: Optional[str]
    error_message: Optional[str]
    task_started_at: Optional[str]
    task_completed_at: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# ===== 需求分析任务相关 =====
class RequirementAnalysisTaskCreate(BaseModel):
    """创建需求分析任务的请求模式"""
    requirement_document_id: int = Field(..., description="需求文档ID")
    prompt_template_id: int = Field(..., description="Prompt模板ID")
    model_config_id: int = Field(..., description="AI模型配置ID")


class RequirementAnalysisTaskResponse(BaseModel):
    """需求分析任务响应模式"""
    id: int
    requirement_document_id: int
    prompt_template_id: int
    model_config_id: int
    status: str
    result: Optional[str]
    error_message: Optional[str]
    tokens_used: Optional[int]
    execution_time: Optional[float]
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# ===== 需求测试分析任务相关 =====
class RequirementTestTaskCreate(BaseModel):
    """创建需求测试分析任务的请求模式"""
    name: str = Field(..., description="任务名称")
    requirement_id: Optional[int] = Field(None, description="关联的需求文档ID")
    requirement_content: Optional[str] = Field(None, description="直接输入的需求内容")
    prompt_template_id: int = Field(..., description="Prompt模板ID")
    model_config_id: int = Field(..., description="AI模型配置ID")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "用户登录功能测试分析",
                    "requirement_content": "用户可以通过用户名密码登录系统",
                    "prompt_template_id": 3,
                    "model_config_id": 1
                }
            ]
        }
    }


class RequirementTestTaskResponse(BaseModel):
    """需求测试分析任务响应模式"""
    id: int
    name: str
    requirement_id: Optional[int]
    requirement_content: Optional[str]
    prompt_template_id: int
    model_config_id: int
    status: str
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    tokens_used: Optional[int]
    execution_time: Optional[float]
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# ===== 状态更新相关 =====
class TaskStatusUpdate(BaseModel):
    """任务状态更新模式"""
    status: str = Field(..., description="任务状态")
    error_message: Optional[str] = Field(None, description="错误信息")


# ===== 文件上传相关 =====
class FileUploadResponse(BaseModel):
    """文件上传响应模式"""
    filename: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小（字节）")
    content: str = Field(..., description="解析后的文本内容")
    

# ===== 查询参数 =====
class RequirementDocumentListParams(BaseModel):
    """需求文档列表查询参数"""
    status: Optional[str] = Field(None, description="状态筛选")
    skip: int = Field(0, description="跳过记录数")
    limit: int = Field(20, description="返回记录数限制")
    
    
class RequirementTestTaskListParams(BaseModel):
    """需求测试任务列表查询参数"""
    status: Optional[str] = Field(None, description="状态筛选")
    skip: int = Field(0, description="跳过记录数")
    limit: int = Field(20, description="返回记录数限制") 