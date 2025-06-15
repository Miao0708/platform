# AI研发辅助平台 - FastAPI后端开发指南

## 🚀 快速开始

### 环境要求
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Git 2.30+

### 项目初始化

#### 1. 创建项目目录
```bash
mkdir ai-platform-backend
cd ai-platform-backend
```

#### 2. 创建虚拟环境
```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 或使用 conda
conda create -n ai-platform python=3.11
conda activate ai-platform
```

#### 3. 安装依赖
```bash
# 创建 requirements.txt
cat > requirements.txt << EOF
# Web框架
fastapi==0.104.1
uvicorn[standard]==0.24.0

# 数据库
sqlmodel==0.0.14
asyncpg==0.29.0
alembic==1.12.1

# 缓存和任务队列
redis==5.0.1
celery==5.3.4

# 认证和安全
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# AI和向量数据库
openai==1.3.7
chromadb==0.4.18
tiktoken==0.5.2

# 工具库
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.25.2

# Git操作
GitPython==3.1.40

# 文件处理
python-magic==0.4.27
PyPDF2==3.0.1

# 日志和监控
structlog==23.2.0
sentry-sdk[fastapi]==1.38.0

# 开发工具
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1
EOF

# 安装依赖
pip install -r requirements.txt
```

#### 4. 项目结构创建
```bash
# 创建项目结构
mkdir -p app/{api/v1,core,models,schemas,services,tasks,utils,tests}
mkdir -p {migrations,scripts,docker,logs}

# 创建 __init__.py 文件
touch app/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/{core,models,schemas,services,tasks,utils,tests}/__init__.py
```

## 🔧 核心配置

### 1. 配置管理 (app/config.py)
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AI研发辅助平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # 数据库配置
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 加密配置
    ENCRYPTION_KEY: str
    
    # AI服务配置
    OPENAI_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    SPARK_API_KEY: Optional[str] = None
    DOUBAO_API_KEY: Optional[str] = None
    
    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: list = [".txt", ".md", ".pdf", ".doc", ".docx"]
    
    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # ChromaDB配置
    CHROMA_DB_PATH: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "ai_platform_knowledge"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2. 数据库连接 (app/database.py)
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# 创建会话工厂
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 3. FastAPI应用入口 (app/main.py)
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import structlog

from app.config import settings
from app.database import init_db
from app.api.v1 import auth, users, ai_models, prompts, requirements, pipelines
from app.middleware import LoggingMiddleware
from app.exceptions import setup_exception_handlers

# 配置日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于AI的研发辅助平台后端API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

app.add_middleware(LoggingMiddleware)

# 设置异常处理器
setup_exception_handlers(app)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(ai_models.router, prefix="/api/v1")
app.include_router(prompts.router, prefix="/api/v1")
app.include_router(requirements.router, prefix="/api/v1")
app.include_router(pipelines.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("应用启动中...")
    await init_db()
    logger.info("数据库初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("应用关闭中...")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用{settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "文档已禁用"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
```

## 🔐 认证系统实现

### 1. 安全工具 (app/core/security.py)
```python
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
```

### 2. 依赖注入 (app/dependencies.py)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.database import get_db
from app.models.user import User
from app.core.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    statement = select(User).where(User.id == user_id, User.is_active == True)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user
```

## 🔄 服务层实现

### 1. 认证服务 (app/services/auth_service.py)
```python
from sqlmodel import Session, select
from typing import Optional
from datetime import timedelta
from app.models.user import User
from app.schemas.auth import Token
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def authenticate_user(self, username: str, password: str) -> Optional[Token]:
        """用户认证"""
        statement = select(User).where(User.username == username, User.is_active == True)
        result = await self.db.execute(statement)
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        # 创建令牌
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Token]:
        """刷新访问令牌"""
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # 验证用户是否存在且活跃
        statement = select(User).where(User.id == user_id, User.is_active == True)
        result = await self.db.execute(statement)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # 创建新的访问令牌
        access_token = create_access_token(data={"sub": user.id})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,  # 保持原刷新令牌
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
```

### 2. AI服务 (app/services/ai_service.py)
```python
import openai
import httpx
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from app.models.ai_model import AIModelConfig
from app.models.requirement import RequirementDocument
from app.core.encryption import encryption_service

class AIService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_ai_client(self, model_config_id: str) -> Dict[str, Any]:
        """获取AI客户端配置"""
        statement = select(AIModelConfig).where(AIModelConfig.id == model_config_id)
        result = await self.db.execute(statement)
        config = result.scalar_one_or_none()
        
        if not config:
            raise ValueError("AI模型配置不存在")
        
        # 解密API密钥
        api_key = encryption_service.decrypt(config.api_key_encrypted)
        
        return {
            "provider": config.provider,
            "base_url": config.base_url,
            "api_key": api_key,
            "model": config.model,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature
        }
    
    async def call_openai_api(self, client_config: Dict[str, Any], messages: list) -> str:
        """调用OpenAI API"""
        client = openai.AsyncOpenAI(
            api_key=client_config["api_key"],
            base_url=client_config["base_url"]
        )
        
        response = await client.chat.completions.create(
            model=client_config["model"],
            messages=messages,
            max_tokens=client_config["max_tokens"],
            temperature=client_config["temperature"]
        )
        
        return response.choices[0].message.content
    
    async def parse_requirement(
        self, 
        requirement_id: str, 
        model_config_id: str, 
        prompt_template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """解析需求文档"""
        # 获取需求文档
        statement = select(RequirementDocument).where(RequirementDocument.id == requirement_id)
        result = await self.db.execute(statement)
        requirement = result.scalar_one_or_none()
        
        if not requirement:
            raise ValueError("需求文档不存在")
        
        # 获取AI客户端配置
        client_config = await self.get_ai_client(model_config_id)
        
        # 构建消息
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的需求分析师，请对用户提供的需求进行分析和优化。"
            },
            {
                "role": "user",
                "content": f"请分析并优化以下需求文档：\n\n{requirement.original_content}"
            }
        ]
        
        # 调用AI API
        if client_config["provider"] == "openai":
            optimized_content = await self.call_openai_api(client_config, messages)
        else:
            # 其他AI服务商的实现
            optimized_content = await self.call_other_ai_api(client_config, messages)
        
        # 更新需求文档
        requirement.optimized_content = optimized_content
        requirement.status = "completed"
        await self.db.commit()
        
        return {
            "original_content": requirement.original_content,
            "optimized_content": optimized_content,
            "status": "completed"
        }
    
    async def test_model_connection(self, model_config_id: str, user_id: str) -> Dict[str, Any]:
        """测试AI模型连接"""
        try:
            client_config = await self.get_ai_client(model_config_id)
            
            # 发送测试消息
            test_messages = [
                {"role": "user", "content": "Hello, this is a connection test."}
            ]
            
            start_time = time.time()
            
            if client_config["provider"] == "openai":
                response = await self.call_openai_api(client_config, test_messages)
            else:
                response = await self.call_other_ai_api(client_config, test_messages)
            
            end_time = time.time()
            latency = round((end_time - start_time) * 1000, 2)  # 毫秒
            
            return {
                "success": True,
                "message": "连接测试成功",
                "latency": latency,
                "response": response[:100] + "..." if len(response) > 100 else response
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"连接测试失败: {str(e)}",
                "latency": None
            }
```

## 🚀 启动和部署

### 1. 开发环境启动
```bash
# 启动PostgreSQL和Redis
docker-compose up -d postgres redis

# 运行数据库迁移
alembic upgrade head

# 启动FastAPI应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动Celery Worker（新终端）
celery -A app.tasks.celery_app worker --loglevel=info

# 启动Celery Beat（定时任务，新终端）
celery -A app.tasks.celery_app beat --loglevel=info
```

### 2. Docker部署
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/ai_platform
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=ai_platform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/ai_platform
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads

volumes:
  postgres_data:
  redis_data:
```

## 📝 开发规范

### 1. 代码格式化
```bash
# 安装开发工具
pip install black isort flake8 mypy

# 格式化代码
black app/
isort app/

# 检查代码质量
flake8 app/
mypy app/
```

### 2. 测试
```bash
# 运行测试
pytest app/tests/ -v

# 生成覆盖率报告
pytest app/tests/ --cov=app --cov-report=html
```

---

**文档版本**: v1.0  
**最后更新**: 2024年12月  
**负责人**: 后端团队
