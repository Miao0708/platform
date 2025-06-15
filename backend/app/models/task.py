"""
任务管理相关数据模型（重构后的三级分离架构）
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, Text, JSON
from app.models.base import BaseModel


class CodeDiffTask(BaseModel, table=True):
    """代码差异任务模型"""
    
    __tablename__ = "code_diff_tasks"
    
    name: str = Field(description="任务名称")
    repository_id: int = Field(foreign_key="repositories.id", description="仓库ID")
    base_ref: str = Field(description="基准分支/提交")
    head_ref: str = Field(description="目标分支/提交")
    
    # 任务状态
    status: str = Field(default="pending", description="状态：pending, processing, completed, failed")
    
    # 结果文件
    diff_file_path: Optional[str] = Field(default=None, description="差异文件存储路径")
    diff_summary: Optional[str] = Field(sa_column=Column(Text), default=None, description="差异摘要")
    
    # 统计信息
    files_changed: Optional[int] = Field(default=None, description="变更文件数")
    lines_added: Optional[int] = Field(default=None, description="新增行数")
    lines_deleted: Optional[int] = Field(default=None, description="删除行数")
    
    # 错误信息
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # 元数据
    task_metadata: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="任务元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "用户登录模块代码差异",
                    "repository_id": 1,
                    "base_ref": "main",
                    "head_ref": "feature/login-enhancement",
                    "status": "completed",
                    "diff_file_path": "/diffs/login_enhancement.diff",
                    "diff_summary": "优化了用户登录流程，添加了双因子认证",
                    "files_changed": 5,
                    "lines_added": 120,
                    "lines_deleted": 30
                }
            ]
        }
    }


class RequirementParseTask(BaseModel, table=True):
    """需求解析任务模型"""
    
    __tablename__ = "requirement_parse_tasks"
    
    name: str = Field(description="任务名称")
    
    # 输入来源
    input_type: str = Field(description="输入类型：text, file")
    original_content: Optional[str] = Field(sa_column=Column(Text), default=None, description="原始文本内容")
    file_path: Optional[str] = Field(default=None, description="上传文件路径")
    file_name: Optional[str] = Field(default=None, description="原始文件名")
    file_size: Optional[int] = Field(default=None, description="文件大小")
    
    # 解析结果
    parsed_content: Optional[str] = Field(sa_column=Column(Text), default=None, description="解析后的需求内容")
    structured_requirements: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="结构化需求")
    
    # 分类和优先级
    category: Optional[str] = Field(default=None, description="需求分类")
    priority: str = Field(default="medium", description="优先级：low, medium, high, urgent")
    complexity: Optional[str] = Field(default=None, description="复杂度：simple, medium, complex")
    estimated_hours: Optional[float] = Field(default=None, description="预估工时")
    
    # 任务状态
    status: str = Field(default="pending", description="状态：pending, processing, completed, failed")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # LLM处理信息
    llm_model: Optional[str] = Field(default=None, description="使用的LLM模型")
    tokens_used: Optional[int] = Field(default=None, description="使用的token数量")
    processing_time: Optional[float] = Field(default=None, description="处理时间（秒）")
    
    # 元数据
    task_metadata: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="任务元数据")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "用户登录功能需求解析",
                    "input_type": "file",
                    "file_name": "login_requirements.docx",
                    "parsed_content": "用户登录功能需要支持多种认证方式...",
                    "structured_requirements": {
                        "functional": [
                            "支持用户名/邮箱登录",
                            "支持双因子认证",
                            "支持记住登录状态"
                        ],
                        "non_functional": [
                            "登录响应时间<2秒",
                            "支持并发1000用户"
                        ]
                    },
                    "category": "authentication",
                    "priority": "high",
                    "complexity": "medium",
                    "estimated_hours": 40.0,
                    "status": "completed"
                }
            ]
        }
    }


class PipelineTask(BaseModel, table=True):
    """流水线任务模型（组合代码和需求）"""
    
    __tablename__ = "pipeline_tasks"
    
    name: str = Field(description="流水线任务名称")
    description: Optional[str] = Field(default=None, description="任务描述")
    
    # 关联的子任务
    code_diff_task_id: Optional[int] = Field(default=None, foreign_key="code_diff_tasks.id", description="代码差异任务ID")
    requirement_task_id: Optional[int] = Field(default=None, foreign_key="requirement_parse_tasks.id", description="需求解析任务ID")

    # 直接关联的资源（兼容旧版本）
    code_diff_id: Optional[int] = Field(default=None, foreign_key="code_diffs.id", description="代码差异ID（直接关联）")
    requirement_text_id: Optional[int] = Field(default=None, foreign_key="requirement_texts.id", description="需求文本ID（直接关联）")
    
    # 流水线配置
    pipeline_type: str = Field(description="流水线类型：code_review, test_generation, documentation")
    prompt_template_id: Optional[int] = Field(default=None, foreign_key="prompt_templates.id", description="Prompt模板ID")
    knowledge_base_id: Optional[int] = Field(default=None, foreign_key="knowledge_bases.id", description="知识库ID")
    
    # 执行配置
    config: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="执行配置")
    
    # 任务状态
    status: str = Field(default="pending", description="状态：pending, queued, running, completed, failed, cancelled")
    
    # 执行结果
    result: Optional[str] = Field(sa_column=Column(Text), default=None, description="执行结果")
    result_data: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="结构化结果数据")
    
    # 执行信息
    started_at: Optional[str] = Field(default=None, description="开始时间")
    completed_at: Optional[str] = Field(default=None, description="完成时间")
    execution_time: Optional[float] = Field(default=None, description="执行时间（秒）")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    
    # LLM使用信息
    llm_model: Optional[str] = Field(default=None, description="使用的LLM模型")
    tokens_used: Optional[int] = Field(default=None, description="使用的token数量")
    
    # 元数据
    task_metadata: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="任务元数据")
    
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
                    "status": "completed",
                    "result": "代码评审完成，发现3个需要关注的问题",
                    "result_data": {
                        "issues_found": 3,
                        "security_score": 85,
                        "quality_score": 90,
                        "suggestions": ["添加输入验证", "优化数据库查询"]
                    },
                    "execution_time": 45.5,
                    "llm_model": "gpt-4",
                    "tokens_used": 3500
                }
            ]
        }
    }


class TaskExecution(BaseModel, table=True):
    """任务执行记录模型"""
    
    __tablename__ = "task_executions"
    
    # 关联任务（可以是任意类型的任务）
    task_type: str = Field(description="任务类型：code_diff, requirement_parse, pipeline")
    task_id: int = Field(description="任务ID")
    execution_id: str = Field(description="执行ID（UUID）", index=True)
    
    # 执行状态
    status: str = Field(description="执行状态：running, completed, failed, cancelled")
    started_at: Optional[str] = Field(default=None, description="开始时间")
    completed_at: Optional[str] = Field(default=None, description="完成时间")
    
    # 执行进度
    steps_total: int = Field(default=0, description="总步骤数")
    steps_completed: int = Field(default=0, description="已完成步骤数")
    current_step: Optional[str] = Field(default=None, description="当前步骤")
    progress_percentage: float = Field(default=0.0, description="进度百分比")
    
    # 结果和日志
    result: Optional[str] = Field(sa_column=Column(Text), default=None, description="执行结果")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    logs: Optional[str] = Field(sa_column=Column(Text), default=None, description="执行日志")
    
    # 资源使用情况
    resources_used: Optional[dict] = Field(sa_column=Column(JSON), default=None, description="资源使用情况")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task_type": "pipeline",
                    "task_id": 1,
                    "execution_id": "exec_123e4567-e89b-12d3-a456-426614174000",
                    "status": "completed",
                    "started_at": "2024-01-01T10:00:00Z",
                    "completed_at": "2024-01-01T10:15:30Z",
                    "steps_total": 5,
                    "steps_completed": 5,
                    "current_step": "生成报告",
                    "progress_percentage": 100.0,
                    "result": "流水线执行完成",
                    "resources_used": {
                        "llm_tokens": 3500,
                        "processing_time": 930,
                        "memory_peak": "256MB"
                    }
                }
            ]
        }
    }
