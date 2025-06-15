"""
API v1 路由汇总
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, git_config, prompt_templates, knowledge_base, code_review, tasks,
    ai_models, conversations, dashboard, users, requirements, ai_prompts
)

api_router = APIRouter()

# 用户认证相关路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["用户认证"]
)

# 用户管理相关路由（适配前端）
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["用户管理"]
)

# 简化的用户接口路由（适配前端调用）
api_router.include_router(
    users.router,
    prefix="/user",
    tags=["用户管理-简化接口"]
)

# AI模型配置相关路由（适配前端）
api_router.include_router(
    ai_models.router,
    prefix="/ai",
    tags=["AI模型配置"]
)

# AI对话相关路由（适配前端）
api_router.include_router(
    conversations.router,
    prefix="/ai",
    tags=["AI对话"]
)

# AI Prompt模板相关路由（适配前端）
api_router.include_router(
    ai_prompts.router,
    prefix="/ai",
    tags=["AI Prompt模板"]
)

# 需求管理相关路由（适配前端）
api_router.include_router(
    requirements.router,
    prefix="/requirements",
    tags=["需求管理"]
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
    tags=["Prompt模板（旧版）"]
)

# 知识库管理相关路由
api_router.include_router(
    knowledge_base.router,
    prefix="/knowledge-bases",
    tags=["知识库管理"]
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
    tags=["代码评审流水线（旧版）"]
)
