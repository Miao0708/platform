# AI研发辅助平台 - 后端API设计文档

## 📋 技术架构

### 核心技术栈
- **Web框架**: FastAPI 0.104+
- **数据库ORM**: SQLModel (SQLAlchemy + Pydantic)
- **数据库**: PostgreSQL 15+
- **缓存**: Redis 7+
- **任务队列**: Celery + Redis
- **向量数据库**: ChromaDB
- **认证**: JWT (JSON Web Tokens)
- **加密**: cryptography (Fernet)
- **异步**: asyncio + asyncpg

### 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI 应用层                            │
│  认证中间件 + CORS + 异常处理 + 请求验证                      │
├─────────────────────────────────────────────────────────────┤
│                    业务逻辑层                                │
│  用户服务 + AI服务 + Git服务 + 需求服务 + 流水线服务          │
├─────────────────────────────────────────────────────────────┤
│                    数据访问层                                │
│  SQLModel ORM + Redis缓存 + ChromaDB向量库                  │
├─────────────────────────────────────────────────────────────┤
│                    外部服务层                                │
│  OpenAI API + DeepSeek API + Git API + 文件存储              │
├─────────────────────────────────────────────────────────────┤
│                    基础设施层                                │
│  PostgreSQL + Redis + Celery + 对象存储                     │
└─────────────────────────────────────────────────────────────┘
```

## 🗂️ 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── dependencies.py         # 依赖注入
│   ├── middleware.py           # 中间件
│   ├── exceptions.py           # 异常处理
│   │
│   ├── models/                 # SQLModel数据模型
│   │   ├── __init__.py
│   │   ├── base.py            # 基础模型
│   │   ├── user.py            # 用户模型
│   │   ├── ai_model.py        # AI模型配置
│   │   ├── prompt.py          # Prompt模板
│   │   ├── requirement.py     # 需求文档
│   │   ├── code_diff.py       # 代码差异
│   │   ├── pipeline.py        # 流水线任务
│   │   └── knowledge.py       # 知识库
│   │
│   ├── schemas/                # Pydantic数据模式
│   │   ├── __init__.py
│   │   ├── base.py            # 基础模式
│   │   ├── user.py            # 用户相关模式
│   │   ├── ai.py              # AI相关模式
│   │   ├── auth.py            # 认证模式
│   │   └── response.py        # 响应模式
│   │
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   ├── v1/                # API v1版本
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # 认证接口
│   │   │   ├── users.py       # 用户管理
│   │   │   ├── ai_models.py   # AI模型配置
│   │   │   ├── prompts.py     # Prompt模板
│   │   │   ├── requirements.py # 需求管理
│   │   │   ├── code_diff.py   # 代码差异
│   │   │   ├── pipelines.py   # 流水线
│   │   │   ├── chat.py        # AI对话
│   │   │   └── knowledge.py   # 知识库
│   │   └── deps.py            # API依赖
│   │
│   ├── services/               # 业务服务层
│   │   ├── __init__.py
│   │   ├── auth_service.py    # 认证服务
│   │   ├── user_service.py    # 用户服务
│   │   ├── ai_service.py      # AI服务
│   │   ├── git_service.py     # Git服务
│   │   ├── requirement_service.py # 需求服务
│   │   ├── pipeline_service.py # 流水线服务
│   │   └── knowledge_service.py # 知识库服务
│   │
│   ├── core/                   # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py        # 安全相关
│   │   ├── encryption.py      # 加密解密
│   │   ├── jwt.py             # JWT处理
│   │   └── permissions.py     # 权限控制
│   │
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py          # 日志配置
│   │   ├── validators.py      # 数据验证
│   │   ├── formatters.py      # 数据格式化
│   │   └── helpers.py         # 辅助函数
│   │
│   ├── tasks/                  # Celery任务
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery应用
│   │   ├── ai_tasks.py        # AI相关任务
│   │   ├── git_tasks.py       # Git相关任务
│   │   └── pipeline_tasks.py  # 流水线任务
│   │
│   └── tests/                  # 测试
│       ├── __init__.py
│       ├── conftest.py        # 测试配置
│       ├── test_auth.py       # 认证测试
│       ├── test_users.py      # 用户测试
│       └── test_ai.py         # AI功能测试
│
├── migrations/                 # 数据库迁移
├── scripts/                    # 脚本文件
├── docker/                     # Docker配置
├── requirements.txt            # 依赖列表
├── requirements-dev.txt        # 开发依赖
├── .env.example               # 环境变量示例
├── docker-compose.yml         # Docker Compose
├── Dockerfile                 # Docker镜像
└── README.md                  # 项目说明
```

## 🔧 核心配置

### 环境变量配置 (.env)
```bash
# 应用配置
APP_NAME=AI研发辅助平台
APP_VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_platform
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 加密配置
ENCRYPTION_KEY=your-fernet-encryption-key

# AI服务配置
OPENAI_API_KEY=your-openai-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
SPARK_API_KEY=your-spark-api-key
DOUBAO_API_KEY=your-doubao-api-key

# 文件存储配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.txt,.md,.pdf,.doc,.docx

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# ChromaDB配置
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=ai_platform_knowledge

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

## 📊 数据模型设计

### 基础模型 (app/models/base.py)
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class BaseModel(SQLModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    is_deleted: bool = Field(default=False)
    
    class Config:
        from_attributes = True
```

### 用户模型 (app/models/user.py)
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from enum import Enum
from .base import BaseModel

class UserRole(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    TESTER = "tester"
    USER = "user"

class User(BaseModel, table=True):
    __tablename__ = "users"
    
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    last_login: Optional[datetime] = None
    
    # 关联关系
    ai_model_configs: List["AIModelConfig"] = Relationship(back_populates="user")
    prompt_templates: List["PromptTemplate"] = Relationship(back_populates="user")
    requirements: List["RequirementDocument"] = Relationship(back_populates="user")
```

### AI模型配置 (app/models/ai_model.py)
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum
from .base import BaseModel

class AIProvider(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    SPARK = "spark"
    DOUBAO = "doubao"
    GEMINI = "gemini"
    CLAUDE = "claude"

class AIModelConfig(BaseModel, table=True):
    __tablename__ = "ai_model_configs"
    
    name: str
    provider: AIProvider
    base_url: str
    api_key_encrypted: str  # 加密存储
    model: str
    max_tokens: Optional[int] = Field(default=4096)
    temperature: Optional[float] = Field(default=0.7)
    is_default: bool = Field(default=False)
    is_active: bool = Field(default=True)
    
    # 外键
    user_id: str = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="ai_model_configs")
```

### Prompt模板 (app/models/prompt.py)
```python
from sqlmodel import SQLModel, Field, Relationship, JSON
from typing import Optional, List
from enum import Enum
from .base import BaseModel

class PromptCategory(str, Enum):
    REQUIREMENT = "requirement"
    CODE_REVIEW = "code_review"
    TEST_CASE = "test_case"
    GENERAL = "general"

class PromptTemplate(BaseModel, table=True):
    __tablename__ = "prompt_templates"
    
    name: str
    identifier: str = Field(unique=True, index=True)
    content: str
    description: Optional[str] = None
    category: PromptCategory
    tags: List[str] = Field(default=[], sa_column=JSON)
    variables: List[str] = Field(default=[], sa_column=JSON)
    is_public: bool = Field(default=False)
    usage_count: int = Field(default=0)
    
    # 外键
    user_id: str = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="prompt_templates")
```

## 🔐 认证与安全

### JWT认证 (app/core/jwt.py)
```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
```

### 加密服务 (app/core/encryption.py)
```python
from cryptography.fernet import Fernet
from app.config import settings

class EncryptionService:
    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def encrypt(self, data: str) -> str:
        """加密字符串"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密字符串"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

encryption_service = EncryptionService()
```

## 🚀 API接口设计

### 认证接口 (app/api/v1/auth.py)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.schemas.auth import Token, UserLogin, UserRegister
from app.services.auth_service import AuthService
from app.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    auth_service = AuthService(db)
    token = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    return token

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    auth_service = AuthService(db)
    token = await auth_service.refresh_access_token(refresh_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效"
        )
    return token

@router.post("/logout")
async def logout():
    """用户登出"""
    return {"message": "登出成功"}
```

### AI模型配置接口 (app/api/v1/ai_models.py)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from app.schemas.ai import AIModelConfigCreate, AIModelConfigUpdate, AIModelConfigResponse
from app.services.ai_service import AIModelService
from app.dependencies import get_db, get_current_user
from app.models.user import User

router = APIRouter(prefix="/ai/models", tags=["AI模型配置"])

@router.get("/", response_model=List[AIModelConfigResponse])
async def get_ai_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取AI模型配置列表"""
    service = AIModelService(db)
    return await service.get_user_models(current_user.id)

@router.post("/", response_model=AIModelConfigResponse)
async def create_ai_model(
    model_data: AIModelConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建AI模型配置"""
    service = AIModelService(db)
    return await service.create_model(model_data, current_user.id)

@router.post("/{model_id}/test")
async def test_ai_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """测试AI模型连接"""
    service = AIModelService(db)
    result = await service.test_model_connection(model_id, current_user.id)
    return result
```

## 🔄 异步任务设计

### Celery配置 (app/tasks/celery_app.py)
```python
from celery import Celery
from app.config import settings

celery_app = Celery(
    "ai_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.ai_tasks",
        "app.tasks.git_tasks",
        "app.tasks.pipeline_tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    task_soft_time_limit=25 * 60,  # 25分钟软超时
)
```

### AI任务 (app/tasks/ai_tasks.py)
```python
from celery import current_task
from app.tasks.celery_app import celery_app
from app.services.ai_service import AIService
from app.database import get_db

@celery_app.task(bind=True)
def parse_requirement_task(self, requirement_id: str, model_config_id: str, prompt_template_id: str = None):
    """异步解析需求任务"""
    try:
        # 更新任务状态
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "开始解析需求..."}
        )
        
        db = next(get_db())
        ai_service = AIService(db)
        
        # 执行AI解析
        result = ai_service.parse_requirement(requirement_id, model_config_id, prompt_template_id)
        
        current_task.update_state(
            state="SUCCESS",
            meta={"current": 100, "total": 100, "status": "需求解析完成", "result": result}
        )
        
        return result
        
    except Exception as exc:
        current_task.update_state(
            state="FAILURE",
            meta={"current": 0, "total": 100, "status": f"解析失败: {str(exc)}"}
        )
        raise exc

@celery_app.task(bind=True)
def code_review_task(self, code_diff_id: str, requirement_id: str, model_config_id: str):
    """异步代码评审任务"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "开始代码评审..."}
        )
        
        db = next(get_db())
        ai_service = AIService(db)
        
        # 执行代码评审
        result = ai_service.review_code(code_diff_id, requirement_id, model_config_id)
        
        current_task.update_state(
            state="SUCCESS",
            meta={"current": 100, "total": 100, "status": "代码评审完成", "result": result}
        )
        
        return result
        
    except Exception as exc:
        current_task.update_state(
            state="FAILURE",
            meta={"current": 0, "total": 100, "status": f"评审失败: {str(exc)}"}
        )
        raise exc
```

## 📈 性能优化

### Redis缓存策略
```python
from redis import Redis
from app.config import settings
import json
import pickle

class CacheService:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
    
    async def get(self, key: str):
        """获取缓存"""
        data = self.redis.get(key)
        if data:
            return pickle.loads(data)
        return None
    
    async def set(self, key: str, value, ttl: int = settings.REDIS_CACHE_TTL):
        """设置缓存"""
        self.redis.setex(key, ttl, pickle.dumps(value))
    
    async def delete(self, key: str):
        """删除缓存"""
        self.redis.delete(key)
    
    async def get_user_models(self, user_id: str):
        """获取用户AI模型配置（带缓存）"""
        cache_key = f"user_models:{user_id}"
        cached_data = await self.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库获取数据
        # ... 数据库查询逻辑
        
        # 缓存结果
        await self.set(cache_key, result)
        return result
```

### 数据库连接池
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

**文档版本**: v1.0  
**最后更新**: 2024年12月  
**负责人**: 后端团队


# AI研发辅助平台 - 数据库设计文档

## 📊 数据库概述

### 技术选型
- **数据库**: PostgreSQL 15+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **迁移工具**: Alembic
- **连接池**: asyncpg + SQLAlchemy异步引擎

### 设计原则
- **规范化**: 遵循第三范式，减少数据冗余
- **性能优化**: 合理使用索引，优化查询性能
- **扩展性**: 支持水平和垂直扩展
- **安全性**: 敏感数据加密存储
- **审计**: 记录数据变更历史

## 🗃️ 数据表设计

### 1. 用户管理

#### users (用户表)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar TEXT,
    department VARCHAR(100),
    position VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'developer', 'tester', 'user')),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
```

#### user_sessions (用户会话表)
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_refresh_token_hash ON user_sessions(refresh_token_hash);
```

### 2. AI模型配置

#### ai_model_configs (AI模型配置表)
```sql
CREATE TABLE ai_model_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('openai', 'deepseek', 'spark', 'doubao', 'gemini', 'claude')),
    base_url TEXT NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    model VARCHAR(100) NOT NULL,
    max_tokens INTEGER DEFAULT 4096,
    temperature DECIMAL(3,2) DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 2),
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_ai_model_configs_user_id ON ai_model_configs(user_id);
CREATE INDEX idx_ai_model_configs_provider ON ai_model_configs(provider);
CREATE INDEX idx_ai_model_configs_is_active ON ai_model_configs(is_active);
CREATE UNIQUE INDEX idx_ai_model_configs_user_default ON ai_model_configs(user_id) WHERE is_default = true;
```

### 3. Prompt模板

#### prompt_templates (Prompt模板表)
```sql
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    identifier VARCHAR(100) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    description TEXT,
    category VARCHAR(20) NOT NULL CHECK (category IN ('requirement', 'code_review', 'test_case', 'general')),
    tags JSONB DEFAULT '[]',
    variables JSONB DEFAULT '[]',
    is_public BOOLEAN DEFAULT false,
    usage_count INTEGER DEFAULT 0,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_prompt_templates_user_id ON prompt_templates(user_id);
CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX idx_prompt_templates_is_public ON prompt_templates(is_public);
CREATE INDEX idx_prompt_templates_identifier ON prompt_templates(identifier);
CREATE INDEX idx_prompt_templates_tags ON prompt_templates USING GIN(tags);
```

### 4. 需求管理

#### requirement_documents (需求文档表)
```sql
CREATE TABLE requirement_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    original_content TEXT NOT NULL,
    optimized_content TEXT,
    source VARCHAR(20) DEFAULT 'manual' CHECK (source IN ('upload', 'manual')),
    original_filename VARCHAR(255),
    file_path TEXT,
    file_size INTEGER,
    mime_type VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    parse_task_id UUID,
    error_message TEXT,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_requirement_documents_user_id ON requirement_documents(user_id);
CREATE INDEX idx_requirement_documents_status ON requirement_documents(status);
CREATE INDEX idx_requirement_documents_source ON requirement_documents(source);
CREATE INDEX idx_requirement_documents_created_at ON requirement_documents(created_at);
```

### 5. Git配置

#### git_credentials (Git凭证表)
```sql
CREATE TABLE git_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    git_username VARCHAR(100) NOT NULL,
    git_email VARCHAR(100) NOT NULL,
    access_token_encrypted TEXT NOT NULL,
    provider VARCHAR(20) DEFAULT 'github' CHECK (provider IN ('github', 'gitlab', 'gitee', 'bitbucket')),
    is_default BOOLEAN DEFAULT false,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_git_credentials_user_id ON git_credentials(user_id);
CREATE INDEX idx_git_credentials_provider ON git_credentials(provider);
CREATE UNIQUE INDEX idx_git_credentials_user_default ON git_credentials(user_id) WHERE is_default = true;
```

#### git_repositories (Git仓库表)
```sql
CREATE TABLE git_repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alias VARCHAR(100) NOT NULL,
    repository_url TEXT NOT NULL,
    branch VARCHAR(100) DEFAULT 'main',
    credential_id UUID REFERENCES git_credentials(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(20) DEFAULT 'pending' CHECK (sync_status IN ('pending', 'syncing', 'success', 'failed')),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_git_repositories_user_id ON git_repositories(user_id);
CREATE INDEX idx_git_repositories_credential_id ON git_repositories(credential_id);
CREATE INDEX idx_git_repositories_is_active ON git_repositories(is_active);
```

### 6. 代码差异

#### code_diff_tasks (代码差异任务表)
```sql
CREATE TABLE code_diff_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    repository_id UUID NOT NULL REFERENCES git_repositories(id) ON DELETE CASCADE,
    compare_type VARCHAR(20) NOT NULL CHECK (compare_type IN ('branch', 'commit')),
    source_ref VARCHAR(100) NOT NULL,
    target_ref VARCHAR(100) NOT NULL,
    diff_content TEXT,
    diff_stats JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_code_diff_tasks_user_id ON code_diff_tasks(user_id);
CREATE INDEX idx_code_diff_tasks_repository_id ON code_diff_tasks(repository_id);
CREATE INDEX idx_code_diff_tasks_status ON code_diff_tasks(status);
CREATE INDEX idx_code_diff_tasks_created_at ON code_diff_tasks(created_at);
```

### 7. 流水线任务

#### pipeline_tasks (流水线任务表)
```sql
CREATE TABLE pipeline_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('code_review', 'test_generation', 'requirement_analysis')),
    code_diff_task_id UUID REFERENCES code_diff_tasks(id) ON DELETE SET NULL,
    requirement_document_id UUID REFERENCES requirement_documents(id) ON DELETE SET NULL,
    prompt_template_id UUID REFERENCES prompt_templates(id) ON DELETE SET NULL,
    ai_model_config_id UUID REFERENCES ai_model_configs(id) ON DELETE SET NULL,
    knowledge_base_id UUID,
    config JSONB DEFAULT '{}',
    result JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    celery_task_id UUID,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_pipeline_tasks_user_id ON pipeline_tasks(user_id);
CREATE INDEX idx_pipeline_tasks_type ON pipeline_tasks(type);
CREATE INDEX idx_pipeline_tasks_status ON pipeline_tasks(status);
CREATE INDEX idx_pipeline_tasks_code_diff_task_id ON pipeline_tasks(code_diff_task_id);
CREATE INDEX idx_pipeline_tasks_requirement_document_id ON pipeline_tasks(requirement_document_id);
CREATE INDEX idx_pipeline_tasks_created_at ON pipeline_tasks(created_at);
```

### 8. AI对话

#### ai_conversations (AI对话表)
```sql
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    ai_model_config_id UUID NOT NULL REFERENCES ai_model_configs(id) ON DELETE CASCADE,
    total_tokens INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP WITH TIME ZONE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX idx_ai_conversations_ai_model_config_id ON ai_conversations(ai_model_config_id);
CREATE INDEX idx_ai_conversations_last_message_at ON ai_conversations(last_message_at);
```

#### ai_messages (AI消息表)
```sql
CREATE TABLE ai_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens INTEGER,
    prompt_template_id UUID REFERENCES prompt_templates(id) ON DELETE SET NULL,
    context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_ai_messages_conversation_id ON ai_messages(conversation_id);
CREATE INDEX idx_ai_messages_role ON ai_messages(role);
CREATE INDEX idx_ai_messages_created_at ON ai_messages(created_at);
```

### 9. 知识库

#### knowledge_bases (知识库表)
```sql
CREATE TABLE knowledge_bases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    collection_name VARCHAR(100) UNIQUE NOT NULL,
    document_count INTEGER DEFAULT 0,
    total_size BIGINT DEFAULT 0,
    is_public BOOLEAN DEFAULT false,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_knowledge_bases_user_id ON knowledge_bases(user_id);
CREATE INDEX idx_knowledge_bases_is_public ON knowledge_bases(is_public);
CREATE INDEX idx_knowledge_bases_collection_name ON knowledge_bases(collection_name);
```

#### knowledge_documents (知识文档表)
```sql
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id UUID NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100),
    content_hash VARCHAR(64),
    chunk_count INTEGER DEFAULT 0,
    processing_status VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT false
);

-- 索引
CREATE INDEX idx_knowledge_documents_knowledge_base_id ON knowledge_documents(knowledge_base_id);
CREATE INDEX idx_knowledge_documents_user_id ON knowledge_documents(user_id);
CREATE INDEX idx_knowledge_documents_processing_status ON knowledge_documents(processing_status);
CREATE INDEX idx_knowledge_documents_content_hash ON knowledge_documents(content_hash);
```

### 10. 系统日志

#### system_logs (系统日志表)
```sql
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level VARCHAR(10) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    module VARCHAR(100),
    function_name VARCHAR(100),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    request_id UUID,
    ip_address INET,
    user_agent TEXT,
    extra_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX idx_system_logs_module ON system_logs(module);

-- 分区表（按月分区）
CREATE TABLE system_logs_y2024m01 PARTITION OF system_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## 🔧 数据库优化

### 1. 索引策略
```sql
-- 复合索引
CREATE INDEX idx_pipeline_tasks_user_status ON pipeline_tasks(user_id, status);
CREATE INDEX idx_ai_messages_conversation_created ON ai_messages(conversation_id, created_at);

-- 部分索引
CREATE INDEX idx_users_active_username ON users(username) WHERE is_active = true;
CREATE INDEX idx_ai_model_configs_active ON ai_model_configs(user_id) WHERE is_active = true;

-- 表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
CREATE INDEX idx_prompt_templates_search ON prompt_templates USING gin(to_tsvector('english', name || ' ' || description));
```

### 2. 分区策略
```sql
-- 按时间分区日志表
CREATE TABLE system_logs (
    id UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- 其他字段...
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE system_logs_y2024m01 PARTITION OF system_logs
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE system_logs_y2024m02 PARTITION OF system_logs
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 3. 性能优化
```sql
-- 启用统计信息自动收集
ALTER TABLE users SET (autovacuum_analyze_scale_factor = 0.05);
ALTER TABLE ai_messages SET (autovacuum_analyze_scale_factor = 0.02);

-- 设置表的填充因子
ALTER TABLE users SET (fillfactor = 90);
ALTER TABLE ai_conversations SET (fillfactor = 85);

-- 创建物化视图
CREATE MATERIALIZED VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    COUNT(DISTINCT ac.id) as conversation_count,
    COUNT(DISTINCT pt.id) as template_count,
    COUNT(DISTINCT rd.id) as requirement_count,
    SUM(ac.total_tokens) as total_tokens_used
FROM users u
LEFT JOIN ai_conversations ac ON u.id = ac.user_id AND ac.is_deleted = false
LEFT JOIN prompt_templates pt ON u.id = pt.user_id AND pt.is_deleted = false
LEFT JOIN requirement_documents rd ON u.id = rd.user_id AND rd.is_deleted = false
WHERE u.is_deleted = false
GROUP BY u.id, u.username;

-- 创建唯一索引
CREATE UNIQUE INDEX idx_user_stats_id ON user_stats(id);

-- 定期刷新物化视图
CREATE OR REPLACE FUNCTION refresh_user_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats;
END;
$$ LANGUAGE plpgsql;
```

## 🔒 安全设计

### 1. 数据加密
```sql
-- 启用行级安全
ALTER TABLE ai_model_configs ENABLE ROW LEVEL SECURITY;

-- 创建安全策略
CREATE POLICY user_ai_models_policy ON ai_model_configs
FOR ALL TO authenticated_users
USING (user_id = current_setting('app.current_user_id')::uuid);

-- 敏感字段加密存储
-- api_key_encrypted 字段使用应用层加密
-- access_token_encrypted 字段使用应用层加密
```

### 2. 审计日志
```sql
-- 创建审计触发器
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, operation, new_data, user_id, created_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW), 
                current_setting('app.current_user_id', true)::uuid, 
                CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, operation, old_data, new_data, user_id, created_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW),
                current_setting('app.current_user_id', true)::uuid,
                CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, operation, old_data, user_id, created_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD),
                current_setting('app.current_user_id', true)::uuid,
                CURRENT_TIMESTAMP);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 为重要表添加审计触发器
CREATE TRIGGER audit_users_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_ai_model_configs_trigger
AFTER INSERT OR UPDATE OR DELETE ON ai_model_configs
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

## 📊 监控和维护

### 1. 性能监控
```sql
-- 查询慢查询
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### 2. 数据清理
```sql
-- 定期清理软删除的数据
CREATE OR REPLACE FUNCTION cleanup_soft_deleted_data()
RETURNS void AS $$
BEGIN
    -- 清理30天前软删除的数据
    DELETE FROM users WHERE is_deleted = true AND updated_at < NOW() - INTERVAL '30 days';
    DELETE FROM ai_model_configs WHERE is_deleted = true AND updated_at < NOW() - INTERVAL '30 days';
    DELETE FROM prompt_templates WHERE is_deleted = true AND updated_at < NOW() - INTERVAL '30 days';
    -- 其他表...
END;
$$ LANGUAGE plpgsql;

-- 定期清理过期的会话
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;
```

---

