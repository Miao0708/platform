"""
用户管理API端点（极简版）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.crud.crud_user import user
from app.schemas.user import UserResponse, UserUpdate, PasswordChange, MessageResponse
from app.core.security import verify_password, get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户详细资料"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_info(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """更新当前用户信息"""
    updated_user = user.update(db=db, db_obj=current_user, obj_in=user_in)
    return updated_user


@router.post("/me/change-password", response_model=MessageResponse)
def change_user_password(
    *,
    db: Session = Depends(get_db),
    password_data: PasswordChange,
    current_user: UserResponse = Depends(get_current_user)
):
    """修改用户密码"""
    # 验证新密码确认
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码与确认密码不匹配"
        )
    
    # 验证当前密码
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.add(current_user)
    db.commit()
    
    return MessageResponse(message="密码修改成功")
