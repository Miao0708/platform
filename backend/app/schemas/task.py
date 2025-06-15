"""
任务管理相关API数据模式（重构后的三级分离架构）
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import UploadFile


# ===== 代码差异任务相关 =====
class CodeDiffTaskCreate(BaseModel):
    """创建代码差异任务的请求模式"""
    name: str = Field(..., description="任务名称")
    repository_id: int = Field(..., description="仓库ID")
    base_ref: str = Field(..., description="基准分支/提交")
    head_ref: str = Field(..., description="目标分支/提交")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="任务元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "用户登录模块代码差异",
                    "repository_id": 1,
                    "base_ref": "main",
                    "head_ref": "feature/login-enhancement",
                    "task_metadata": {
                        "description": "优化用户登录流程",
                        "reviewer": "张三"
                    }
                }
            ]
        }
    }


class CodeDiffTaskResponse(BaseModel):
    """代码差异任务响应模式"""
    id: int
    name: str
    repository_id: int
    base_ref: str
    head_ref: str
    status: str
    diff_file_path: Optional[str]
    diff_summary: Optional[str]
    files_changed: Optional[int]
    lines_added: Optional[int]
    lines_deleted: Optional[int]
    error_message: Optional[str]
    task_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class CodeDiffTaskUpdate(BaseModel):
    """更新代码差异任务的请求模式"""
    name: Optional[str] = Field(None, description="任务名称")
    status: Optional[str] = Field(None, description="任务状态")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="任务元数据")


# ===== 需求解析任务相关 =====
class RequirementParseTaskCreate(BaseModel):
    """创建需求解析任务的请求模式"""
    name: str = Field(..., description="任务名称")
    input_type: str = Field(..., description="输入类型：text, file")
    original_content: Optional[str] = Field(None, description="原始文本内容")
    category: Optional[str] = Field(None, description="需求分类")
    priority: str = Field("medium", description="优先级：low, medium, high, urgent")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="任务元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "用户登录功能需求解析",
                    "input_type": "text",
                    "original_content": "用户登录功能需要支持多种认证方式，包括用户名密码、邮箱登录、第三方OAuth等...",
                    "category": "authentication",
                    "priority": "high",
                    "task_metadata": {
                        "source": "产品需求文档",
                        "version": "v2.0"
                    }
                }
            ]
        }
    }


class RequirementParseTaskFileUpload(BaseModel):
    """需求解析任务文件上传请求模式"""
    name: str = Field(..., description="任务名称")
    category: Optional[str] = Field(None, description="需求分类")
    priority: str = Field("medium", description="优先级")
    task_metadata: Optional[str] = Field(None, description="任务元数据JSON字符串")


class RequirementParseTaskResponse(BaseModel):
    """需求解析任务响应模式"""
    id: int
    name: str
    input_type: str
    original_content: Optional[str]
    file_path: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    parsed_content: Optional[str]
    structured_requirements: Optional[Dict[str, Any]]
    category: Optional[str]
    priority: str
    complexity: Optional[str]
    estimated_hours: Optional[float]
    status: str
    error_message: Optional[str]
    llm_model: Optional[str]
    tokens_used: Optional[int]
    processing_time: Optional[float]
    task_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class RequirementParseTaskUpdate(BaseModel):
    """更新需求解析任务的请求模式"""
    name: Optional[str] = Field(None, description="任务名称")
    parsed_content: Optional[str] = Field(None, description="解析后的需求内容")
    category: Optional[str] = Field(None, description="需求分类")
    priority: Optional[str] = Field(None, description="优先级")
    complexity: Optional[str] = Field(None, description="复杂度")
    estimated_hours: Optional[float] = Field(None, description="预估工时")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="任务元数据")


# ===== 流水线任务相关 =====
class PipelineTaskCreate(BaseModel):
    """创建流水线任务的请求模式"""
    name: str = Field(..., description="流水线任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    code_diff_task_id: Optional[int] = Field(None, description="代码差异任务ID")
    requirement_task_id: Optional[int] = Field(None, description="需求解析任务ID")
    pipeline_type: str = Field(..., description="流水线类型：code_review, test_generation, documentation")
    prompt_template_id: Optional[int] = Field(None, description="Prompt模板ID")
    knowledge_base_id: Optional[int] = Field(None, description="知识库ID")
    config: Optional[Dict[str, Any]] = Field(None, description="执行配置")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="任务元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "登录模块代码评审流水线",
                    "description": "对登录模块的代码变更进行安全性和质量评审",
                    "code_diff_task_id": 1,
                    "requirement_task_id": 1,
                    "pipeline_type": "code_review",
                    "prompt_template_id": 1,
                    "knowledge_base_id": 1,
                    "config": {
                        "focus_areas": ["security", "performance"],
                        "severity_threshold": "medium",
                        "include_suggestions": True
                    },
                    "task_metadata": {
                        "reviewer": "张三",
                        "deadline": "2024-01-15"
                    }
                }
            ]
        }
    }


class PipelineTaskResponse(BaseModel):
    """流水线任务响应模式"""
    id: int
    name: str
    description: Optional[str]
    code_diff_task_id: Optional[int]
    requirement_task_id: Optional[int]
    pipeline_type: str
    prompt_template_id: Optional[int]
    knowledge_base_id: Optional[int]
    config: Optional[Dict[str, Any]]
    status: str
    result: Optional[str]
    result_data: Optional[Dict[str, Any]]
    started_at: Optional[str]
    completed_at: Optional[str]
    execution_time: Optional[float]
    error_message: Optional[str]
    llm_model: Optional[str]
    tokens_used: Optional[int]
    task_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


class PipelineTaskUpdate(BaseModel):
    """更新流水线任务的请求模式"""
    name: Optional[str] = Field(None, description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    config: Optional[Dict[str, Any]] = Field(None, description="执行配置")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="任务元数据")


# ===== 任务执行相关 =====
class TaskExecutionResponse(BaseModel):
    """任务执行响应模式"""
    id: int
    task_type: str
    task_id: int
    execution_id: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    steps_total: int
    steps_completed: int
    current_step: Optional[str]
    progress_percentage: float
    result: Optional[str]
    error_message: Optional[str]
    logs: Optional[str]
    resources_used: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class TaskExecutionRequest(BaseModel):
    """任务执行请求模式"""
    config_override: Optional[Dict[str, Any]] = Field(None, description="配置覆盖")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "config_override": {
                        "llm_model": "gpt-4",
                        "max_tokens": 4000,
                        "temperature": 0.7
                    }
                }
            ]
        }
    }


# ===== 任务选择器相关 =====
class TaskSelector(BaseModel):
    """任务选择器模式（用于流水线任务选择代码和需求）"""
    id: int
    name: str
    status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class CodeDiffTaskSelector(TaskSelector):
    """代码差异任务选择器"""
    repository_id: int
    base_ref: str
    head_ref: str
    files_changed: Optional[int]
    lines_added: Optional[int]
    lines_deleted: Optional[int]


class RequirementTaskSelector(TaskSelector):
    """需求解析任务选择器"""
    category: Optional[str]
    priority: str
    complexity: Optional[str]
    estimated_hours: Optional[float]


# ===== 统计信息 =====
class TaskStats(BaseModel):
    """任务统计信息"""
    code_diff_tasks: Dict[str, int] = Field(description="代码差异任务统计")
    requirement_tasks: Dict[str, int] = Field(description="需求解析任务统计")
    pipeline_tasks: Dict[str, int] = Field(description="流水线任务统计")
    total_executions: int = Field(description="总执行次数")
    success_rate: float = Field(description="成功率百分比")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code_diff_tasks": {
                        "total": 50,
                        "pending": 5,
                        "processing": 2,
                        "completed": 40,
                        "failed": 3
                    },
                    "requirement_tasks": {
                        "total": 30,
                        "pending": 3,
                        "processing": 1,
                        "completed": 25,
                        "failed": 1
                    },
                    "pipeline_tasks": {
                        "total": 25,
                        "pending": 2,
                        "running": 1,
                        "completed": 20,
                        "failed": 2
                    },
                    "total_executions": 105,
                    "success_rate": 92.4
                }
            ]
        }
    }
