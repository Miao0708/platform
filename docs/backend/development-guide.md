# 后端开发指南

## 📋 项目概述

基于 FastAPI + SQLModel + PostgreSQL 的 AI 研发辅助平台后端服务，提供高性能的异步 API 和丰富的 AI 集成功能。

## 🛠️ 技术栈

- **Web框架**: FastAPI 0.104.1
- **ASGI服务器**: Uvicorn 0.24.0
- **ORM**: SQLModel 0.0.14 (基于 SQLAlchemy + Pydantic)
- **数据库**: PostgreSQL (通过 asyncpg)
- **数据库迁移**: Alembic 1.12.1
- **缓存**: Redis 5.0.1
- **任务队列**: Celery 5.3.4
- **认证**: 简化Token认证系统
- **密码加密**: bcrypt (passlib 1.7.4)
- **AI集成**: OpenAI 1.3.7
- **向量数据库**: ChromaDB 0.4.18
- **Git操作**: GitPython 3.1.40
- **日志**: structlog 23.2.0
- **测试**: pytest 7.4.3

## 📁 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── core/                   # 核心配置和工具
│   │   ├── config.py          # 应用配置
│   │   ├── database.py        # 数据库连接
│   │   ├── security.py        # 安全相关
│   │   └── deps.py            # 依赖注入
│   ├── api/                    # API 路由
│   │   └── v1/                # API v1 版本
│   │       ├── api.py         # 路由汇总
│   │       └── endpoints/     # 具体端点
│   ├── models/                 # SQLModel 数据模型
│   ├── schemas/                # Pydantic 数据模式
│   ├── crud/                   # 数据库操作
│   ├── services/               # 业务服务层
│   └── tasks/                  # Celery 任务
├── chroma_db/                  # ChromaDB 数据目录
├── requirements.txt            # Python 依赖
└── ai_dev_platform.db          # SQLite 数据库文件
```

## 🚀 开发环境搭建

### 环境要求
- Python >= 3.9
- PostgreSQL >= 13 (可选，默认使用 SQLite)
- Redis >= 6.0 (可选)

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 环境配置
创建 `.env` 文件：
```bash
# 应用配置
PROJECT_NAME=AI研发辅助平台
VERSION=1.0.0
DEBUG=True
SECRET_KEY=your-secret-key-here

# 数据库配置 (可选，默认使用 SQLite)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_platform

# Redis配置 (可选)
# REDIS_URL=redis://localhost:6379/0

# 认证配置
ENCRYPTION_KEY=your-32-character-base64-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI 服务配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
```

### 3. 启动开发服务器
```bash
# 启动 FastAPI 服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 启动 Celery Worker (可选)
celery -A app.tasks.celery_app worker --loglevel=info

# 启动 Celery Beat (可选)
celery -A app.tasks.celery_app beat --loglevel=info
```

### 4. 访问 API 文档
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## 📝 开发规范

### 1. 代码风格
- 使用 Black 格式化代码
- 使用 isort 排序导入
- 使用 flake8 检查代码质量
- 使用 mypy 进行类型检查

```bash
# 格式化代码
black app/
isort app/

# 代码质量检查
flake8 app/
mypy app/
```

### 2. 数据模型定义 (SQLModel)
```python
# app/models/user.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # 关系定义
    ai_models: List["AIModel"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
```

### 3. API 路由定义
```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from app.core.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=UserInDB)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """创建新用户"""
    service = UserService(db)
    return await service.create_user(user)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户信息"""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.get("/", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户列表"""
    service = UserService(db)
    return await service.list_users(skip=skip, limit=limit)

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用户信息"""
    service = UserService(db)
    user = await service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除用户"""
    service = UserService(db)
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return {"message": "用户删除成功"}
```

### 4. 业务服务层
```python
# app/services/user_service.py
from sqlmodel import Session, select
from typing import Optional, List
from passlib.context import CryptContext

from app.models.user import User, UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user_create: UserCreate) -> User:
        """创建新用户"""
        hashed_password = pwd_context.hash(user_create.password)
        
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            is_active=user_create.is_active
        )
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        statement = select(User).where(User.id == user_id)
        result = await self.db.exec(statement)
        return result.first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        result = await self.db.exec(statement)
        return result.first()
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        statement = select(User).offset(skip).limit(limit)
        result = await self.db.exec(statement)
        return result.all()
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = await self.get_user(user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        db_user = await self.get_user(user_id)
        if not db_user:
            return False
        
        await self.db.delete(db_user)
        await self.db.commit()
        return True
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = await self.get_user_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
```

### 5. 数据库配置
```python
# app/core/database.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 同步引擎 (用于 Alembic)
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+asyncpg", ""),
    echo=settings.DEBUG
)

# 异步引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# 异步会话工厂
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

def create_db_and_tables():
    """创建数据库表"""
    SQLModel.metadata.create_all(sync_engine)

async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session
```

### 6. 认证系统配置

```python
# app/core/security.py
import secrets
from datetime import datetime, timedelta
from typing import Optional, Union
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 加密实例
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())

def create_access_token(
    subject: Union[str, int], expires_delta: Optional[timedelta] = None
) -> str:
    """创建简单的访问令牌（使用随机字符串）"""
    # 生成随机token
    token = secrets.token_urlsafe(32)
    return f"{subject}:{token}:{int(datetime.utcnow().timestamp())}"

def verify_token(token: str) -> Optional[str]:
    """验证令牌并返回用户ID"""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None

        user_id, token_part, timestamp = parts

        # 检查token是否过期（30天）
        token_time = datetime.fromtimestamp(int(timestamp))
        if datetime.utcnow() - token_time > timedelta(days=30):
            return None

        return user_id
    except (ValueError, Exception):
        return None
```

### 7. 依赖注入
```python
# app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.services.user_service import UserService
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    service = UserService(db)
    user = await service.get_user_by_username(username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
```

## 🤖 AI 服务集成

### OpenAI 集成示例
```python
# app/services/ai_service.py
import openai
from typing import List, Dict, Any
from app.core.config import settings

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        openai.api_base = settings.OPENAI_BASE_URL
    
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """AI 对话完成"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"AI 服务调用失败: {str(e)}"
            )
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gpt-3.5-turbo"
    ):
        """流式 AI 对话"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                stream=True
            )
            
            async for chunk in response:
                if chunk.choices[0].delta.get("content"):
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            yield f"错误: {str(e)}"
```

## 🧪 测试

### 单元测试示例
```python
# tests/test_user_service.py
import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from app.models.user import User, UserCreate
from app.services.user_service import UserService

@pytest.fixture
def session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session

@pytest.mark.asyncio
async def test_create_user(session: Session):
    """测试创建用户"""
    service = UserService(session)
    
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword",
        full_name="Test User"
    )
    
    user = await service.create_user(user_create)
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.id is not None

@pytest.mark.asyncio
async def test_authenticate_user(session: Session):
    """测试用户认证"""
    service = UserService(session)
    
    # 创建用户
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword"
    )
    await service.create_user(user_create)
    
    # 测试认证
    user = await service.authenticate_user("testuser", "testpassword")
    assert user is not None
    assert user.username == "testuser"
    
    # 测试错误密码
    user = await service.authenticate_user("testuser", "wrongpassword")
    assert user is None
```

### API 测试示例
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_user():
    """测试创建用户 API"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
```

## 📦 部署和运维

### Docker 配置
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/ai_platform
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ai_platform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 📚 最佳实践

### 1. 错误处理
```python
from fastapi import HTTPException
from app.core.exceptions import CustomException

# 自定义异常
class UserNotFoundError(CustomException):
    def __init__(self, user_id: int):
        super().__init__(f"用户 {user_id} 不存在")

# 统一错误处理
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)}
    )
```

### 2. 日志配置
```python
import structlog
from app.core.config import settings

# 配置结构化日志
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
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

### 3. 性能优化
- 使用数据库连接池
- 实现查询结果缓存
- 使用异步操作
- 合理使用数据库索引
- 实现 API 限流

### 4. 安全最佳实践
- 使用 HTTPS
- 实现 CORS 配置
- 输入数据验证
- SQL 注入防护
- 敏感信息加密存储

## 🔗 学习资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [SQLModel 官方文档](https://sqlmodel.tiangolo.com/)
- [Pydantic 官方文档](https://pydantic-docs.helpmanual.io/)
- [AsyncIO 编程指南](https://docs.python.org/3/library/asyncio.html) 