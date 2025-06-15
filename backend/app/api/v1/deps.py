"""
FastAPI依赖项
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from app.core.database import get_session
from app.core.security import verify_token


# HTTP Bearer认证
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话依赖项"""
    yield from get_session()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> str:
    """获取当前用户依赖项"""
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def get_current_active_user(
    current_user: str = Depends(get_current_user)
) -> str:
    """获取当前活跃用户依赖项"""
    # 这里可以添加用户状态检查逻辑
    return current_user
