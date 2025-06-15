"""
API v1版本路由聚合器
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, git_config, prompt_templates, knowledge_base, code_review, tasks,
    ai_models, conversations, dashboard, users, requirements, ai_prompts,
    requirement_management
)

api_router = APIRouter()

# 用户认证相关路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["用户认证"]
)

# 用户管理相关路由（标准RESTful路径）
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户管理"]
)

# AI模型配置相关路由（适配前端）
api_router.include_router(
    ai_models.router,
    prefix="/ai/models",
    tags=["AI模型"]
)

# AI对话相关路由（适配前端）
api_router.include_router(
    conversations.router,
    prefix="/conversations",
    tags=["对话管理"]
)

# AI Prompt模板相关路由（适配前端）
api_router.include_router(
    ai_prompts.router,
    prefix="/ai/prompts",
    tags=["AI提示词"]
)

# 需求管理相关路由（适配前端）
api_router.include_router(
    requirements.router,
    prefix="/old-requirements",
    tags=["旧需求管理"]
)

# 新的需求管理系统
api_router.include_router(
    requirement_management.router,
    prefix="/requirement-management",
    tags=["需求管理系统"]
)

# 仪表盘统计相关路由（适配前端）
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["仪表盘"]
)

# Git配置相关路由
api_router.include_router(
    git_config.router,
    prefix="/git",
    tags=["Git配置"]
)

# Prompt模板相关路由（旧版，保留兼容性）
api_router.include_router(
    prompt_templates.router,
    prefix="/prompt-templates",
    tags=["Prompt模板"]
)

# 知识库管理相关路由
api_router.include_router(
    knowledge_base.router,
    prefix="/knowledge-base",
    tags=["知识库"]
)

# 三级分离任务管理相关路由
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["任务管理"]
)

# 代码评审流水线相关路由（保留兼容性）
api_router.include_router(
    code_review.router,
    prefix="/code-review",
    tags=["代码审查"]
)
