# API接口链路调试指南

## 🎯 概述

本系统提供了完整的前后端API调试功能，可以详细追踪每个API请求的完整链路，包括：

- 📥 **请求详情**: 方法、URL、请求头、请求体、查询参数
- 📤 **响应详情**: 状态码、响应头、响应数据、处理时间
- 🗄️ **数据库操作**: SQL查询、执行时间、参数
- 💥 **错误信息**: 异常堆栈、错误上下文
- 🔗 **链路追踪**: 唯一请求ID，便于关联前后端日志

## 🚀 启动调试模式

### 方法1: 使用调试脚本（推荐）
```powershell
# 在项目根目录执行
.\debug-start.ps1
```

### 方法2: 手动启动

#### 后端调试模式
```powershell
cd backend
$env:DEBUG = "true"
$env:LOG_LEVEL = "DEBUG"
uvicorn app.main:app --reload --port=8000 --log-level debug
```

#### 前端调试模式
```powershell
cd frontend
npm run dev
# 然后在浏览器中打开开发者工具查看Console日志
```

## 📋 日志格式说明

### 后端日志示例

#### 📥 HTTP请求日志
```
📥 HTTP请求详情
request_id: req_1704067200123
method: POST
url: http://localhost:8000/api/v1/git/repositories
path: /api/v1/git/repositories
client_host: 127.0.0.1
user_agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
headers: {
  "content-type": "application/json",
  "authorization": "***",
  "accept": "application/json"
}
query_params: {}
body: {
  "name": "test-repo",
  "url": "https://github.com/user/repo.git",
  "branch": "main"
}
timestamp: 2024-01-01T12:00:00.123Z
```

#### 📤 HTTP响应日志
```
📤 HTTP响应详情
request_id: req_1704067200123
status_code: 200
headers: {
  "content-type": "application/json",
  "content-length": "156"
}
process_time_ms: 45.67
timestamp: 2024-01-01T12:00:00.168Z
```

#### 🗄️ 数据库查询日志
```
🗄️ 数据库查询
query: INSERT INTO repositories (name, url, branch, created_at) VALUES (?, ?, ?, ?)
params: ["test-repo", "https://github.com/user/repo.git", "main", "2024-01-01T12:00:00.123Z"]
execution_time_ms: 12.34
timestamp: 2024-01-01T12:00:00.135Z
```

### 前端日志示例

#### 📤 API请求日志
```javascript
📤 API请求 [req_1704067200123_abc123]
🔗 POST http://localhost:8000/api/v1/git/repositories
📋 请求头: {
  "Content-Type": "application/json",
  "Authorization": "***",
  "Accept": "application/json"
}
📦 请求体: {
  "name": "test-repo",
  "url": "https://github.com/user/repo.git",
  "branch": "main"
}
⏰ 发送时间: 2024-01-01T12:00:00.123Z
```

#### 📥 API响应日志
```javascript
📥 API响应 [req_1704067200123_abc123] ✅
📊 状态: 200 OK
⏱️ 耗时: 156ms
📋 响应头: {
  "content-type": "application/json",
  "content-length": "156"
}
📦 响应数据: {
  "code": 200,
  "message": "success",
  "data": {
    "id": "123",
    "name": "test-repo",
    "url": "https://github.com/user/repo.git"
  }
}
⏰ 接收时间: 2024-01-01T12:00:00.279Z
```

## 🔍 调试技巧

### 1. 过滤特定API
在浏览器控制台中：
```javascript
// 只显示包含"git"的API请求
console.group = (function(originalGroup) {
  return function(label) {
    if (label.includes('git') || label.includes('Git')) {
      return originalGroup.call(console, label);
    }
  };
})(console.group);
```

### 2. 监控API性能
```javascript
// 监控耗时超过100ms的请求
const originalLog = console.log;
console.log = function(label, ...args) {
  if (typeof label === 'string' && label.includes('⏱️ 耗时')) {
    const timeMatch = label.match(/(\d+)ms/);
    if (timeMatch && parseInt(timeMatch[1]) > 100) {
      originalLog.call(console, `🐌 慢请求警告: ${label}`, ...args);
    }
  }
  return originalLog.call(console, label, ...args);
};
```

### 3. 追踪请求链路
通过requestId关联前后端日志：
1. 前端发起请求时生成requestId（如：`req_1704067200123_abc123`）
2. 后端接收到请求时记录对应的requestId（如：`req_1704067200123`）
3. 通过时间戳匹配前后端日志

### 4. 错误调试
当API调用失败时，查看以下信息：
- 前端错误日志中的详细错误信息
- 后端日志中的异常堆栈
- 数据库操作是否成功
- 网络连接状态

## 📊 性能分析

### 请求耗时分析
- **< 50ms**: 🟢 优秀
- **50-200ms**: 🟡 良好  
- **200-500ms**: 🟠 需优化
- **> 500ms**: 🔴 性能问题

### 数据库查询分析
- **< 10ms**: 🟢 优秀
- **10-50ms**: 🟡 良好
- **50-100ms**: 🟠 需优化
- **> 100ms**: 🔴 需要索引优化

## 🛠️ 配置选项

### 后端配置
在 `backend/app/core/config.py` 中：
```python
# 调试模式
DEBUG: bool = True

# 日志级别
LOG_LEVEL: str = "DEBUG"

# 日志文件（可选）
LOG_FILE: str = "./logs/app.log"
```

### 前端配置
在 `frontend/src/utils/request-logger.ts` 中：
```javascript
// 启用/禁用日志
requestLogger.setEnabled(true);

// 在生产环境中自动禁用
const logger = new RequestLogger(import.meta.env.DEV);
```

## ⚠️ 注意事项

1. **敏感信息过滤**: 自动过滤`authorization`、`cookie`等敏感请求头
2. **性能影响**: 调试模式会影响性能，生产环境请关闭
3. **日志存储**: 大量日志可能占用磁盘空间，建议定期清理
4. **网络安全**: 不要在日志中记录用户密码等敏感数据

## 📝 自定义日志

### 添加业务日志
```python
# 后端
from app.core.logging import logger

logger.info("📋 业务操作", 
    operation="create_user",
    user_id="123",
    details={"email": "user@example.com"}
)
```

```javascript
// 前端
console.group('📋 业务操作');
console.log('操作类型:', 'create_user');
console.log('用户ID:', '123');
console.log('详情:', {email: 'user@example.com'});
console.groupEnd();
```

这个调试系统将帮助你快速定位和解决API相关的问题，提高开发效率！ 