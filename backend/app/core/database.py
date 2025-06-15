"""
数据库连接和会话管理
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


# 同步数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}  # SQLite特定配置
)

# 异步数据库引擎
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}
)

# 异步会话工厂
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


def create_db_and_tables():
    """创建数据库表"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """获取同步数据库会话"""
    with Session(engine) as session:
        yield session


async def get_async_session():
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


# 数据库依赖项
def get_db():
    """FastAPI依赖项：获取数据库会话"""
    return get_session()


async def get_async_db():
    """FastAPI依赖项：获取异步数据库会话"""
    async for session in get_async_session():
        yield session
