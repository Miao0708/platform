# 🚀 AI研发辅助平台 - 本地开发配置指南

## 📋 配置修复内容

根据您的反馈，我已经完成了前后端跨域配置的检查和优化，确保支持本地启动和联调测试。

### 🔧 主要配置调整

#### 1. **前端配置优化**
- ✅ **统一端口配置**：将 `package.json` 和 `vite.config.js` 端口统一为 3000
- ✅ **添加代理配置**：在 `vite.config.js` 中添加后端 API 代理，解决跨域问题
- ✅ **环境适配**：API 请求根据开发/生产环境自动选择基础路径
- ✅ **类型定义**：添加 `vite-env.d.ts` 解决 TypeScript 类型问题

#### 2. **后端配置优化**
- ✅ **CORS 配置**：根据环境变量配置允许的前端域名
- ✅ **环境变量支持**：添加 `ALLOWED_ORIGINS` 配置项
- ✅ **开发日志**：在 DEBUG 模式下添加请求日志中间件
- ✅ **配置示例**：创建 `env.example` 环境变量配置模板

#### 3. **联调支持**
- ✅ **启动脚本**：创建 Linux/macOS (`start-dev.sh`) 和 Windows (`start-dev.ps1`) 启动脚本
- ✅ **自动化检查**：脚本自动检查依赖环境和配置文件
- ✅ **密钥生成**：自动生成所需的安全密钥示例

## 🌐 网络配置详情

### 前端配置 (Port: 3000)
```javascript
// vite.config.js
server: {
  port: 3000,
  host: '0.0.0.0',
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false
    }
  }
}
```

### 后端配置 (Port: 8000)
```python
# CORS配置
allowed_origins = settings.allowed_origins_list if not settings.DEBUG else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
```

## 🚀 快速启动方法

### 方法一：使用启动脚本（推荐）

**Linux/macOS:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

**Windows:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\start-dev.ps1
```

### 方法二：手动启动

#### 1. 后端环境配置
```bash
# 复制环境配置模板
cp backend/env.example backend/.env

# 编辑 .env 文件，设置必要的配置
# 特别是 SECRET_KEY 和 ENCRYPTION_KEY

# 生成密钥示例：
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

#### 2. 启动后端服务
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

## 🔗 访问地址

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/v1/docs
- **健康检查**: http://localhost:8000/health

## ✅ 验证联调

### 1. 检查服务状态
- 前端: 访问 http://localhost:3000 确认页面正常加载
- 后端: 访问 http://localhost:8000/health 应返回 `{"status": "healthy"}`

### 2. 测试跨域请求
- 在前端应用中发起 API 请求
- 检查浏览器开发者工具的 Network 面板
- 确认请求正常发送且无 CORS 错误

### 3. 查看日志
- 后端控制台会显示请求日志（DEBUG 模式下）
- 前端控制台会显示 API 请求响应信息

## 📝 环境变量配置

### 后端 (.env)
```env
# 必需配置
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# 开发配置
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# 可选配置
LLM_API_KEY=your-openai-api-key
DATABASE_URL=sqlite:///./ai_dev_platform.db
REDIS_URL=redis://localhost:6379/0
```

### 前端环境变量 (如需要)
```env
# .env.local
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=AI研发辅助平台
```

## 🐛 常见问题解决

### 1. 端口冲突
- 修改 `vite.config.js` 中的端口配置
- 修改 `backend/app/core/config.py` 中的 CORS 配置

### 2. CORS 错误
- 检查后端 `ALLOWED_ORIGINS` 配置
- 确认前端请求地址与后端 CORS 配置匹配

### 3. 环境变量错误
- 确保 `backend/.env` 文件存在且配置正确
- 检查 SECRET_KEY 和 ENCRYPTION_KEY 是否设置

### 4. 依赖安装问题
- 删除 `node_modules` 重新安装前端依赖
- 重新创建 Python 虚拟环境安装后端依赖

## 🎯 下一步

现在您的项目已经支持本地联调，您可以：
1. 测试现有的 API 功能
2. 开发新的功能模块
3. 进行前后端集成测试
4. 添加更多的业务逻辑

如有任何问题，请查看控制台日志或检查以上配置是否正确。 