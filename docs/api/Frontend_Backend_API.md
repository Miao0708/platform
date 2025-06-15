# 前后端联调API接口文档

## 📋 接口概述

### 基础信息
- **API版本**: v1
- **基础URL**: `http://localhost:8000/api/v1`
- **认证方式**: Bearer Token (JWT)
- **数据格式**: JSON

### 通用响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2024-12-01T10:00:00Z"
}
```

## 🔐 1. 认证接口

### 1.1 用户登录
```
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

**请求参数**
```
username=admin&password=admin123
```

**响应数据**
```json
{
  "code": 200,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "1",
      "username": "admin",
      "email": "admin@example.com",
      "nickname": "管理员",
      "role": "admin"
    }
  }
}
```

### 1.2 刷新Token
```
POST /auth/refresh
```

**请求参数**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 1.3 登出
```
POST /auth/logout
Authorization: Bearer {access_token}
```

## 👤 2. 用户管理接口

### 2.1 获取当前用户信息
```
GET /users/me
Authorization: Bearer {access_token}
```

**响应数据**
```json
{
  "code": 200,
  "data": {
    "id": "1",
    "username": "admin",
    "email": "admin@example.com",
    "nickname": "管理员",
    "avatar": "https://example.com/avatar.jpg",
    "department": "技术部",
    "position": "高级工程师",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 2.2 更新用户信息
```
PUT /users/me
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "email": "new@example.com",
  "nickname": "新昵称",
  "department": "产品部",
  "position": "产品经理"
}
```

### 2.3 修改密码
```
PUT /users/me/password
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "current_password": "old_password",
  "new_password": "new_password"
}
```

### 2.4 上传头像
```
POST /users/me/avatar
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求参数**
- `file`: 图片文件

## 🤖 3. AI模型配置接口

### 3.1 获取AI模型列表
```
GET /ai/models
Authorization: Bearer {access_token}
```

**响应数据**
```json
{
  "code": 200,
  "data": [
    {
      "id": "1",
      "name": "OpenAI GPT-4o",
      "provider": "openai",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4o",
      "max_tokens": 4096,
      "temperature": 0.7,
      "is_default": true,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 3.2 创建AI模型配置
```
POST /ai/models
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "name": "DeepSeek Chat",
  "provider": "deepseek",
  "base_url": "https://api.deepseek.com/v1",
  "api_key": "sk-xxx",
  "model": "deepseek-chat",
  "max_tokens": 4096,
  "temperature": 0.7,
  "is_default": false,
  "is_active": true
}
```

### 3.3 更新AI模型配置
```
PUT /ai/models/{model_id}
Authorization: Bearer {access_token}
```

### 3.4 删除AI模型配置
```
DELETE /ai/models/{model_id}
Authorization: Bearer {access_token}
```

### 3.5 测试AI模型连接
```
POST /ai/models/{model_id}/test
Authorization: Bearer {access_token}
```

**响应数据**
```json
{
  "code": 200,
  "data": {
    "success": true,
    "message": "连接测试成功",
    "latency": 150
  }
}
```

### 3.6 设置默认模型
```
POST /ai/models/{model_id}/set-default
Authorization: Bearer {access_token}
```

## 📝 4. Prompt模板接口

### 4.1 获取Prompt模板列表
```
GET /ai/prompts
Authorization: Bearer {access_token}
```

**查询参数**
- `category`: 分类筛选 (requirement/code_review/test_case/general)
- `tags`: 标签筛选 (多个用逗号分隔)
- `is_public`: 是否公开
- `keyword`: 关键词搜索

**响应数据**
```json
{
  "code": 200,
  "data": [
    {
      "id": "1",
      "name": "代码评审专家",
      "identifier": "code_review_expert",
      "content": "你是一个资深的代码评审专家...",
      "description": "专业的代码评审模板",
      "category": "code_review",
      "tags": ["代码评审", "安全检查"],
      "variables": ["code_diff", "requirement"],
      "is_public": true,
      "usage_count": 156,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 4.2 创建Prompt模板
```
POST /ai/prompts
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "name": "需求分析师",
  "identifier": "requirement_analyst",
  "content": "你是一个专业的需求分析师，请分析以下需求：\n\n{{requirement}}",
  "description": "专业的需求分析模板",
  "category": "requirement",
  "tags": ["需求分析", "功能设计"],
  "is_public": true
}
```

### 4.3 更新Prompt模板
```
PUT /ai/prompts/{prompt_id}
Authorization: Bearer {access_token}
```

### 4.4 删除Prompt模板
```
DELETE /ai/prompts/{prompt_id}
Authorization: Bearer {access_token}
```

### 4.5 渲染Prompt模板
```
POST /ai/prompts/{prompt_id}/render
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "variables": {
    "requirement": "用户登录功能需求",
    "code_diff": "diff --git a/login.js..."
  }
}
```

## 💬 5. AI对话接口

### 5.1 获取对话列表
```
GET /ai/conversations
Authorization: Bearer {access_token}
```

**响应数据**
```json
{
  "code": 200,
  "data": [
    {
      "id": "1",
      "title": "代码评审讨论",
      "model_config_id": "1",
      "total_tokens": 1250,
      "message_count": 8,
      "last_message_at": "2024-01-01T10:30:00Z",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### 5.2 创建对话
```
POST /ai/conversations
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "title": "新的对话",
  "model_config_id": "1"
}
```

### 5.3 获取对话详情
```
GET /ai/conversations/{conversation_id}
Authorization: Bearer {access_token}
```

**响应数据**
```json
{
  "code": 200,
  "data": {
    "id": "1",
    "title": "代码评审讨论",
    "model_config_id": "1",
    "messages": [
      {
        "id": "1",
        "role": "user",
        "content": "请帮我评审这段代码",
        "timestamp": "2024-01-01T10:00:00Z",
        "tokens": 10
      },
      {
        "id": "2",
        "role": "assistant",
        "content": "这段代码整体结构清晰...",
        "timestamp": "2024-01-01T10:01:00Z",
        "tokens": 150
      }
    ],
    "total_tokens": 160
  }
}
```

### 5.4 发送消息
```
POST /ai/conversations/{conversation_id}/messages
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "content": "请帮我分析这个需求",
  "model_config_id": "1",
  "prompt_template_id": "2",
  "context": {
    "requirement": "用户登录功能",
    "code_diff": "diff内容"
  }
}
```

### 5.5 更新对话标题
```
PUT /ai/conversations/{conversation_id}
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "title": "新的对话标题"
}
```

### 5.6 删除对话
```
DELETE /ai/conversations/{conversation_id}
Authorization: Bearer {access_token}
```

## 📋 6. 需求管理接口

### 6.1 获取需求列表
```
GET /requirements
Authorization: Bearer {access_token}
```

**查询参数**
- `status`: 状态筛选 (pending/processing/completed/failed)
- `source`: 来源筛选 (upload/manual)
- `keyword`: 关键词搜索

**响应数据**
```json
{
  "code": 200,
  "data": [
    {
      "id": "1",
      "name": "用户登录功能需求",
      "original_content": "用户需要能够登录系统...",
      "optimized_content": "## 用户登录功能需求\n\n### 功能描述...",
      "source": "upload",
      "original_filename": "login_requirement.md",
      "status": "completed",
      "parse_task_id": "task_1",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### 6.2 创建需求
```
POST /requirements
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "name": "支付功能需求",
  "original_content": "用户需要能够在线支付...",
  "source": "manual"
}
```

### 6.3 上传需求文档
```
POST /requirements/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求参数**
- `file`: 需求文档文件
- `name`: 需求名称

### 6.4 更新需求
```
PUT /requirements/{requirement_id}
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "name": "更新的需求名称",
  "original_content": "更新的原始内容",
  "optimized_content": "更新的优化内容"
}
```

### 6.5 删除需求
```
DELETE /requirements/{requirement_id}
Authorization: Bearer {access_token}
```

### 6.6 AI解析需求
```
POST /requirements/{requirement_id}/parse
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "model_config_id": "1",
  "prompt_template_id": "2"
}
```

**响应数据**
```json
{
  "code": 200,
  "data": {
    "task_id": "parse_task_123",
    "status": "running"
  }
}
```

## 🔧 7. Git配置接口

### 7.1 获取Git凭证列表
```
GET /git/credentials
Authorization: Bearer {access_token}
```

### 7.2 创建Git凭证
```
POST /git/credentials
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "name": "GitHub凭证",
  "git_username": "username",
  "git_email": "user@example.com",
  "access_token": "ghp_xxxxxxxxxxxx",
  "provider": "github",
  "is_default": true
}
```

### 7.3 测试Git凭证
```
POST /git/credentials/{credential_id}/test
Authorization: Bearer {access_token}
```

### 7.4 获取Git仓库列表
```
GET /git/repositories
Authorization: Bearer {access_token}
```

### 7.5 创建Git仓库
```
POST /git/repositories
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "alias": "主项目仓库",
  "repository_url": "https://github.com/user/repo.git",
  "branch": "main",
  "credential_id": "1"
}
```

### 7.6 测试Git仓库连接
```
POST /git/repositories/{repository_id}/test
Authorization: Bearer {access_token}
```

## 🔍 8. 代码Diff接口

### 8.1 获取Diff任务列表
```
GET /code-diff/tasks
Authorization: Bearer {access_token}
```

### 8.2 创建Diff任务
```
POST /code-diff/tasks
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "name": "登录功能代码对比",
  "repository_id": "1",
  "compare_type": "branch",
  "source_ref": "feature/login",
  "target_ref": "main"
}
```

### 8.3 执行Diff任务
```
POST /code-diff/tasks/{task_id}/execute
Authorization: Bearer {access_token}
```

### 8.4 获取Diff结果
```
GET /code-diff/tasks/{task_id}/result
Authorization: Bearer {access_token}
```

## 🔄 9. 流水线接口

### 9.1 获取流水线任务列表
```
GET /pipelines/tasks
Authorization: Bearer {access_token}
```

### 9.2 创建流水线任务
```
POST /pipelines/tasks
Authorization: Bearer {access_token}
```

**请求参数**
```json
{
  "name": "用户登录代码评审",
  "type": "code_review",
  "code_diff_task_id": "1",
  "requirement_document_id": "1",
  "prompt_template_id": "1",
  "ai_model_config_id": "1",
  "knowledge_base_id": "1"
}
```

### 9.3 执行流水线任务
```
POST /pipelines/tasks/{task_id}/execute
Authorization: Bearer {access_token}
```

### 9.4 获取任务结果
```
GET /pipelines/tasks/{task_id}/result
Authorization: Bearer {access_token}
```

## 📊 10. 任务状态接口

### 10.1 获取任务状态
```
GET /tasks/{task_id}/status
Authorization: Bearer {access_token}
```

**响应数据**
```json
{
  "code": 200,
  "data": {
    "status": "running",
    "progress": 65,
    "message": "正在分析代码差异...",
    "start_time": "2024-01-01T10:00:00Z",
    "estimated_time": 120
  }
}
```

### 10.2 取消任务
```
POST /tasks/{task_id}/cancel
Authorization: Bearer {access_token}
```

## 📁 11. 文件上传接口

### 11.1 通用文件上传
```
POST /upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**请求参数**
- `file`: 文件
- `type`: 文件类型 (avatar/document/attachment)

## 📈 12. 仪表盘接口

### 12.1 获取仪表盘数据
```
GET /dashboard/stats
Authorization: Bearer {access_token}
```

**响应数据**
```json
{
  "code": 200,
  "data": {
    "total_tasks": 156,
    "completed_tasks": 142,
    "running_tasks": 8,
    "failed_tasks": 6,
    "total_tokens_used": 125000,
    "recent_tasks": [
      {
        "id": "1",
        "name": "代码评审任务",
        "type": "code_review",
        "status": "completed",
        "created_at": "2024-01-01T10:00:00Z"
      }
    ]
  }
}
```

---

**前端对接优先级**：
1. **认证接口** (登录/登出/用户信息)
2. **AI模型配置** (CRUD操作)
3. **Prompt模板管理** (CRUD操作)
4. **AI对话功能** (对话管理和消息发送)
5. **需求管理** (文档上传和AI解析)
6. **其他功能** (Git配置、流水线等)
