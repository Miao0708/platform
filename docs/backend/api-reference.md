# API 参考文档

## 📋 概述

AI 研发辅助平台后端 API 基于 FastAPI 构建，提供 RESTful API 接口，支持自动生成的 OpenAPI 3.0 文档。

## 🔗 API 端点

- **Base URL**: `http://localhost:8000`
- **API Version**: `v1`
- **API Prefix**: `/api/v1`
- **文档地址**: 
  - Swagger UI: `http://localhost:8000/api/v1/docs`
  - ReDoc: `http://localhost:8000/api/v1/redoc`
  - OpenAPI Schema: `http://localhost:8000/api/v1/openapi.json`

## 🔐 认证

所有需要认证的 API 都使用简化的Bearer Token 认证。

### 认证头部
```http
Authorization: Bearer <your-access-token>
```

### 获取 Token
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

## 📚 API 端点详情

### 1. 认证相关 API

#### 1.1 用户登录
```http
POST /api/v1/auth/login
```

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "full_name": "string",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 1.2 用户注册
```http
POST /api/v1/auth/register
```

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

#### 1.3 刷新 Token
```http
POST /api/v1/auth/refresh
```

**请求头**:
```http
Authorization: Bearer <refresh-token>
```

### 2. 用户管理 API

#### 2.1 获取当前用户信息
```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 2.2 更新用户信息
```http
PUT /api/v1/users/me
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "full_name": "string",
  "email": "string"
}
```

#### 2.3 修改密码
```http
POST /api/v1/users/change-password
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

### 3. AI 模型配置 API

#### 3.1 获取 AI 模型列表
```http
GET /api/v1/ai-models/
Authorization: Bearer <token>
```

**查询参数**:
- `skip`: int (default: 0) - 跳过记录数
- `limit`: int (default: 100) - 限制记录数
- `provider`: string (optional) - 服务提供商筛选

**响应**:
```json
[
  {
    "id": 1,
    "name": "GPT-4",
    "provider": "openai",
    "model_name": "gpt-4",
    "api_key": "sk-***",
    "base_url": "https://api.openai.com/v1",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### 3.2 创建 AI 模型配置
```http
POST /api/v1/ai-models/
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "string",
  "provider": "openai",
  "model_name": "gpt-4",
  "api_key": "string",
  "base_url": "string",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

#### 3.3 测试 AI 模型连接
```http
POST /api/v1/ai-models/{model_id}/test
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "message": "连接成功",
  "response_time": 0.5
}
```

### 4. Prompt 模板 API

#### 4.1 获取 Prompt 模板列表
```http
GET /api/v1/prompts/
Authorization: Bearer <token>
```

**查询参数**:
- `skip`: int (default: 0)
- `limit`: int (default: 100)
- `category`: string (optional) - 分类筛选
- `tags`: string (optional) - 标签筛选

**响应**:
```json
[
  {
    "id": 1,
    "title": "代码评审模板",
    "content": "请对以下代码进行评审：\n{{code_diff}}",
    "category": "code_review",
    "tags": ["代码", "评审"],
    "is_public": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### 4.2 创建 Prompt 模板
```http
POST /api/v1/prompts/
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "string",
  "content": "string",
  "category": "string",
  "tags": ["string"],
  "is_public": false,
  "variables": ["{{code_diff}}", "{{requirement}}"]
}
```

#### 4.3 预览 Prompt 模板
```http
POST /api/v1/prompts/{prompt_id}/preview
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "variables": {
    "code_diff": "string",
    "requirement": "string"
  }
}
```

### 5. 需求管理 API

#### 5.1 获取需求列表
```http
GET /api/v1/requirements/
Authorization: Bearer <token>
```

**响应**:
```json
[
  {
    "id": 1,
    "title": "用户登录功能",
    "content": "实现用户登录功能，支持用户名密码登录",
    "original_content": "原始需求内容",
    "optimized_content": "AI 优化后的需求内容",
    "status": "optimized",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### 5.2 创建需求
```http
POST /api/v1/requirements/
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "string",
  "content": "string",
  "source": "manual|upload"
}
```

#### 5.3 AI 优化需求
```http
POST /api/v1/requirements/{requirement_id}/optimize
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "ai_model_id": 1,
  "optimization_type": "clarity|completeness|feasibility"
}
```

### 6. 代码差异 API

#### 6.1 创建代码差异任务
```http
POST /api/v1/code-diff/
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "repository_url": "string",
  "source_branch": "string",
  "target_branch": "string",
  "file_patterns": ["*.py", "*.js"],
  "exclude_patterns": ["*.test.py"]
}
```

**响应**:
```json
{
  "id": 1,
  "task_id": "string",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 6.2 获取代码差异结果
```http
GET /api/v1/code-diff/{diff_id}
Authorization: Bearer <token>
```

**响应**:
```json
{
  "id": 1,
  "status": "completed",
  "result": {
    "files": [
      {
        "path": "src/main.py",
        "change_type": "modified",
        "additions": 10,
        "deletions": 5,
        "diff": "string"
      }
    ],
    "summary": {
      "total_files": 5,
      "total_additions": 50,
      "total_deletions": 20
    }
  },
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:01:00Z"
}
```

### 7. 流水线 API

#### 7.1 创建流水线任务
```http
POST /api/v1/pipelines/
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "name": "代码评审流水线",
  "type": "code_review",
  "config": {
    "code_diff_id": 1,
    "requirement_id": 2,
    "ai_model_id": 1,
    "prompt_template_id": 1,
    "knowledge_base_ids": [1, 2]
  }
}
```

#### 7.2 执行流水线
```http
POST /api/v1/pipelines/{pipeline_id}/execute
Authorization: Bearer <token>
```

**响应**:
```json
{
  "task_id": "string",
  "status": "running",
  "started_at": "2024-01-01T00:00:00Z"
}
```

#### 7.3 获取流水线结果
```http
GET /api/v1/pipelines/{pipeline_id}/results/{task_id}
Authorization: Bearer <token>
```

### 8. AI 对话 API

#### 8.1 创建对话会话
```http
POST /api/v1/chat/sessions/
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "代码评审讨论",
  "ai_model_id": 1
}
```

#### 8.2 发送消息
```http
POST /api/v1/chat/sessions/{session_id}/messages
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "content": "请帮我评审这段代码",
  "context": {
    "code_diff_id": 1,
    "requirement_id": 2
  }
}
```

#### 8.3 流式对话 (WebSocket)
```
WSS /api/v1/chat/sessions/{session_id}/stream
Authorization: Bearer <token>
```

**发送格式**:
```json
{
  "type": "message",
  "content": "string",
  "context": {}
}
```

**接收格式**:
```json
{
  "type": "message|error|done",
  "content": "string",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 9. 知识库 API

#### 9.1 上传文档
```http
POST /api/v1/knowledge/documents/
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求体**:
- `file`: File - 文档文件
- `title`: string - 文档标题
- `category`: string - 文档分类

#### 9.2 文档检索
```http
POST /api/v1/knowledge/search
Authorization: Bearer <token>
```

**请求体**:
```json
{
  "query": "用户认证",
  "limit": 10,
  "threshold": 0.7
}
```

**响应**:
```json
{
  "results": [
    {
      "document_id": 1,
      "title": "用户认证设计文档",
      "content": "相关内容片段",
      "score": 0.95,
      "metadata": {
        "category": "design",
        "created_at": "2024-01-01T00:00:00Z"
      }
    }
  ]
}
```

## 📊 响应格式

### 成功响应
```json
{
  "data": {},
  "message": "操作成功",
  "code": 200
}
```

### 错误响应
```json
{
  "detail": "错误详情",
  "code": 400,
  "type": "validation_error"
}
```

### 分页响应
```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

## 🔧 状态码

- `200` - 成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未认证
- `403` - 权限不足
- `404` - 资源不存在
- `422` - 数据验证错误
- `500` - 服务器内部错误

## 📝 数据模型

### User 模型
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "full_name": "string|null",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime|null"
}
```

### AIModel 模型
```json
{
  "id": "integer",
  "name": "string",
  "provider": "string",
  "model_name": "string",
  "api_key": "string",
  "base_url": "string",
  "parameters": "object",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime|null"
}
```

### PromptTemplate 模型
```json
{
  "id": "integer",
  "title": "string",
  "content": "string",
  "category": "string",
  "tags": "array[string]",
  "variables": "array[string]",
  "is_public": "boolean",
  "usage_count": "integer",
  "created_at": "datetime",
  "updated_at": "datetime|null"
}
```

## 🧪 API 测试

### 使用 curl 测试
```bash
# 登录获取 token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# 使用 token 访问 API
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 使用 Python requests
```python
import requests

# 登录
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "admin", "password": "password"}
)
token = response.json()["access_token"]

# 使用 token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/v1/users/me",
    headers=headers
)
```

## 📖 限制和注意事项

1. **请求频率限制**: 每个用户每分钟最多 100 个请求
2. **文件上传限制**: 单个文件最大 10MB
3. **Token 有效期**: 访问令牌有效期 30 分钟
4. **并发限制**: 同时处理的流水线任务最多 5 个
5. **WebSocket 连接**: 每个用户最多同时 3 个连接

## 🔗 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [OpenAPI 3.0 规范](https://swagger.io/specification/)
- [JWT 规范](https://jwt.io/)
- [WebSocket 协议](https://tools.ietf.org/html/rfc6455) 