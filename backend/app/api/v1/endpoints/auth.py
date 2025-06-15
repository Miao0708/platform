"""
用户认证相关API端点（极简版）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_user import user
from app.schemas.user import UserRegister, UserLogin, UserResponse, MessageResponse
from app.core.security import create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()


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


@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserRegister
):
    """用户注册"""
    try:
        new_user = user.create(db=db, obj_in=user_in)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
def login(
    *,
    db: Session = Depends(get_db),
    user_in: UserLogin
):
    """用户登录"""
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

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": authenticated_user.id,
            "username": authenticated_user.username,
            "is_superuser": authenticated_user.is_superuser
        }
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user


@router.post("/logout", response_model=MessageResponse)
def logout():
    """用户登出"""
    return MessageResponse(message="登出成功")
