"""
用户认证相关API端点（简化版）
"""
from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_user import user
from app.schemas.user import (
    UserRegister, UserLogin, UserResponse,
    UserUpdate, PasswordChange, MessageResponse
)
from app.core.security import create_access_token, verify_token
from app.core.config import settings

router = APIRouter()
security = HTTPBearer()


def get_client_info(request: Request) -> dict:
    """获取客户端信息"""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "device_info": request.headers.get("user-agent", "Unknown")[:100]
    }


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """获取当前用户ID"""
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def get_current_user(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
) -> UserResponse:
    """获取当前用户信息"""
    current_user = user.get(db, int(user_id))
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user


# ===== 认证相关端点 =====
@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserRegister,
    request: Request
):
    """用户注册"""
    try:
        new_user = user.create(db=db, obj_in=user_in)
        
        # 记录注册日志
        client_info = get_client_info(request)
        user_login_log.create_log(
            db=db,
            user_id=new_user.id,
            login_type="register",
            success=True,
            **client_info
        )
        
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/login")
def login(
    *,
    db: Session = Depends(get_db),
    user_in: UserLogin,
    request: Request
):
    """用户登录（简化版）"""
    # 验证用户
    authenticated_user = user.authenticate(
        db, username=user_in.username, password=user_in.password
    )

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if not authenticated_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )

    # 创建访问令牌
    access_token = create_access_token(subject=str(authenticated_user.id))

    # 更新用户登录信息
    user.update_login_info(db, user_id=authenticated_user.id)

    from app.core.response import StandardJSONResponse

    return StandardJSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": access_token,  # 简化：使用同一个token
            "token_type": "bearer",
            "expires_in": 30 * 24 * 3600,  # 30天
            "user": {
                "id": str(authenticated_user.id),
                "username": authenticated_user.username,
                "email": authenticated_user.email,
                "nickname": authenticated_user.full_name,
                "avatar": authenticated_user.avatar_url
            }
        },
        message="登录成功"
    )


@router.post("/refresh")
def refresh_token(
    *,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """刷新访问令牌（简化版）"""
    # 创建新的访问令牌
    new_access_token = create_access_token(subject=str(current_user.id))

    from app.core.response import StandardJSONResponse

    return StandardJSONResponse(
        content={
            "access_token": new_access_token,
            "refresh_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 30 * 24 * 3600,
            "user": {
                "id": str(current_user.id),
                "username": current_user.username,
                "email": current_user.email,
                "nickname": current_user.full_name,
                "avatar": current_user.avatar_url
            }
        },
        message="Token刷新成功"
    )


@router.post("/logout")
def logout(
    *,
    current_user: UserResponse = Depends(get_current_user)
):
    """用户登出（简化版）"""
    from app.core.response import StandardJSONResponse

    return StandardJSONResponse(
        content=None,
        message="登出成功"
    )


# ===== 基本用户信息管理 =====
@router.get("/me")
def read_current_user(
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户信息"""
    from app.core.response import StandardJSONResponse

    return StandardJSONResponse(
        content={
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "nickname": current_user.full_name,
            "avatar": current_user.avatar_url,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        },
        message="获取用户信息成功"
    )
