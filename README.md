# AI开发平台

一个集成前后端的AI开发平台项目，提供代码审查、项目管理和AI辅助开发功能。

## 项目结构

```
E:/web/
├── frontend/                    # 前端项目 (Vue.js + TypeScript)
│   ├── src/                     # 源代码
│   ├── public/                  # 静态资源
│   ├── node_modules/           # Node.js依赖
│   ├── package.json            # 前端依赖配置
│   └── vite.config.js          # Vite构建配置
├── backend/                     # 后端项目 (FastAPI + Python)
│   ├── .venv/                  # Python虚拟环境
│   ├── app/                    # 应用代码
│   ├── chroma_db/              # 向量数据库
│   ├── logs/                   # 日志文件
│   ├── uploads/                # 上传文件
│   ├── pyproject.toml          # Python依赖配置
│   └── ai_dev_platform.db      # SQLite数据库
├── docs/                        # 项目文档
│   ├── api/                     # API文档
│   ├── frontend/                # 前端文档
│   ├── backend/                 # 后端文档
│   ├── deployment/              # 部署文档
│   ├── requirements/            # 需求文档
│   └── development/             # 开发文档
├── .env                         # 环境配置
├── .gitignore                   # Git忽略文件
└── README.md                    # 项目说明
```

## 技术栈

### 前端
- **框架**: Vue.js 3
- **语言**: TypeScript
- **构建工具**: Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router

### 后端
- **框架**: FastAPI
- **语言**: Python 3.8+
- **数据库**: SQLite + ChromaDB (向量数据库)
- **ORM**: SQLModel
- **认证**: 简化Token认证
- **任务队列**: Celery

## 快速开始

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 后端开发

```bash
cd backend
# 激活虚拟环境 (Windows)
.venv\Scripts\activate
# 或者 (Linux/Mac)
source .venv/bin/activate

# 启动服务
uvicorn app.main:app --reload
```

## 开发指南

- 📖 [API文档](./docs/api/)
- 🎨 [前端开发指南](./docs/frontend/)
- ⚙️ [后端开发指南](./docs/backend/)
- 🚀 [部署指南](./docs/deployment/)
- 📋 [需求文档](./docs/requirements/)

## 环境要求

- Node.js 16+
- Python 3.8+
- Git

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE)
