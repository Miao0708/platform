"""
流水线相关API数据模式
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


# ===== 代码差异相关 =====
class CodeDiffCreate(BaseModel):
    """创建代码差异的请求模式"""
    repository_id: int = Field(..., description="仓库ID")
    base_ref: str = Field(..., description="基准分支/提交")
    head_ref: str = Field(..., description="目标分支/提交")
    diff_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "repository_id": 1,
                    "base_ref": "main",
                    "head_ref": "feature/new-api",
                    "diff_metadata": {
                        "description": "新API功能开发",
                        "reviewer": "张三"
                    }
                }
            ]
        }
    }


class CodeDiffResponse(BaseModel):
    """代码差异响应模式"""
    id: int
    repository_id: int
    base_ref: str
    head_ref: str
    diff_file_path: Optional[str]
    status: str
    error_message: Optional[str]
    diff_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# ===== 需求文本相关 =====
class RequirementTextCreate(BaseModel):
    """创建需求文本的请求模式"""
    title: str = Field(..., description="需求标题")
    original_content: str = Field(..., description="原始需求内容")
    category: Optional[str] = Field(None, description="需求分类")
    priority: str = Field("medium", description="优先级：low, medium, high, urgent")
    req_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "用户登录功能优化",
                    "original_content": "需要优化用户登录功能，提高安全性和用户体验，包括添加双因子认证、优化界面设计等",
                    "category": "security",
                    "priority": "high",
                    "req_metadata": {
                        "estimated_hours": 40,
                        "assigned_team": "backend"
                    }
                }
            ]
        }
    }


class RequirementTextUpdate(BaseModel):
    """更新需求文本的请求模式"""
    title: Optional[str] = Field(None, description="需求标题")
    original_content: Optional[str] = Field(None, description="原始需求内容")
    refined_content: Optional[str] = Field(None, description="精炼后的需求内容")
    category: Optional[str] = Field(None, description="需求分类")
    priority: Optional[str] = Field(None, description="优先级")
    status: Optional[str] = Field(None, description="状态")
    req_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class RequirementTextResponse(BaseModel):
    """需求文本响应模式"""
    id: int
    title: str
    original_content: str
    refined_content: Optional[str]
    category: Optional[str]
    priority: str
    status: str
    req_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# ===== 流水线任务相关 =====
class PipelineTaskCreate(BaseModel):
    """创建流水线任务的请求模式"""
    name: str = Field(..., description="任务名称")
    task_type: str = Field(..., description="任务类型：CODE_REVIEW, TEST_CASE, DOCUMENTATION")
    code_diff_id: Optional[int] = Field(None, description="代码差异ID")
    requirement_text_id: Optional[int] = Field(None, description="需求文本ID")
    prompt_template_id: Optional[int] = Field(None, description="Prompt模板ID")
    knowledge_base_id: Optional[int] = Field(None, description="知识库ID")
    config: Optional[Dict[str, Any]] = Field(None, description="任务配置参数")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="任务元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "代码安全评审-登录模块",
                    "task_type": "CODE_REVIEW",
                    "code_diff_id": 1,
                    "requirement_text_id": 1,
                    "prompt_template_id": 1,
                    "knowledge_base_id": 1,
                    "config": {
                        "focus_areas": ["security", "performance"],
                        "severity_threshold": "medium"
                    },
                    "task_metadata": {
                        "reviewer": "张三",
                        "deadline": "2024-01-15"
                    }
                }
            ]
        }
    }


class PipelineTaskUpdate(BaseModel):
    """更新流水线任务的请求模式"""
    name: Optional[str] = Field(None, description="任务名称")
    status: Optional[str] = Field(None, description="任务状态")
    config: Optional[Dict[str, Any]] = Field(None, description="任务配置参数")
    task_metadata: Optional[Dict[str, Any]] = Field(None, description="任务元数据")


class PipelineTaskResponse(BaseModel):
    """流水线任务响应模式"""
    id: int
    name: str
    task_type: str
    status: str
    code_diff_id: Optional[int]
    requirement_text_id: Optional[int]
    prompt_template_id: Optional[int]
    knowledge_base_id: Optional[int]
    result: Optional[str]
    error_message: Optional[str]
    execution_time: Optional[float]
    config: Optional[Dict[str, Any]]
    task_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = {"from_attributes": True}


# ===== 任务执行相关 =====
class TaskExecutionResponse(BaseModel):
    """任务执行响应模式"""
    id: int
    task_id: int
    execution_id: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    steps_total: int
    steps_completed: int
    current_step: Optional[str]
    result: Optional[str]
    error_message: Optional[str]
    logs: Optional[str]
    resources_used: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class TaskExecutionRequest(BaseModel):
    """任务执行请求模式"""
    task_id: int = Field(..., description="任务ID")
    config_override: Optional[Dict[str, Any]] = Field(None, description="配置覆盖")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task_id": 1,
                    "config_override": {
                        "llm_model": "gpt-4",
                        "max_tokens": 4000
                    }
                }
            ]
        }
    }


# ===== 通用响应模式 =====
class TaskProgress(BaseModel):
    """任务进度模式"""
    task_id: int
    execution_id: str
    status: str
    progress: float = Field(description="进度百分比 0-100")
    current_step: str
    steps_completed: int
    steps_total: int
    estimated_remaining_time: Optional[int] = Field(None, description="预计剩余时间（秒）")


class PipelineStats(BaseModel):
    """流水线统计信息"""
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_execution_time: Optional[float]
    success_rate: float = Field(description="成功率百分比")


class CodeReviewResult(BaseModel):
    """代码评审结果模式"""
    summary: str = Field(description="评审摘要")
    issues: List[Dict[str, Any]] = Field(description="发现的问题")
    suggestions: List[str] = Field(description="改进建议")
    security_score: Optional[int] = Field(None, description="安全评分 0-100")
    quality_score: Optional[int] = Field(None, description="质量评分 0-100")
    complexity_analysis: Optional[Dict[str, Any]] = Field(None, description="复杂度分析")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "代码整体质量良好，发现3个需要关注的问题",
                    "issues": [
                        {
                            "type": "security",
                            "severity": "high",
                            "file": "auth.py",
                            "line": 45,
                            "description": "存在SQL注入风险",
                            "suggestion": "使用参数化查询"
                        }
                    ],
                    "suggestions": [
                        "添加输入验证",
                        "增加单元测试覆盖率",
                        "优化数据库查询性能"
                    ],
                    "security_score": 75,
                    "quality_score": 85,
                    "complexity_analysis": {
                        "cyclomatic_complexity": 8,
                        "maintainability_index": 72
                    }
                }
            ]
        }
    }
