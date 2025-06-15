"""
用户管理API端点（适配前端需求）
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.crud.crud_user import user
from app.schemas.user import UserResponse, UserUpdate, UserPreferencesUpdate, PasswordChange
from app.core.response import StandardJSONResponse

router = APIRouter()


@router.get("/me", tags=["用户管理"])
def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """获取当前用户详细资料（重定向到认证会话信息，建议使用 /auth/session）"""
    try:
        # 提供用户管理相关的详细信息，与认证会话信息区分
        user_data = {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "avatar_url": current_user.avatar_url,
            "bio": current_user.bio,
            "preferences": current_user.preferences,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "login_count": current_user.login_count,
            "last_login_at": current_user.last_login_at,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at
        }
        
        return StandardJSONResponse(
            content=user_data,
            message="获取用户详细资料成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取用户详细资料失败: {str(e)}"
        )


@router.put("/me", tags=["用户管理"])
def update_current_user_info(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """更新当前用户信息"""
    try:
        updated_user = user.update(db=db, db_obj=current_user, obj_in=user_in)
        
        user_data = {
            "id": str(updated_user.id),
            "username": updated_user.username,
            "email": updated_user.email,
            "full_name": updated_user.full_name,
            "avatar_url": updated_user.avatar_url,
            "bio": updated_user.bio
        }
        
        return StandardJSONResponse(
            content=user_data,
            message="用户信息更新成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"更新用户信息失败: {str(e)}"
        )


@router.put("/me/preferences", tags=["用户管理"])
def update_user_preferences(
    *,
    db: Session = Depends(get_db),
    preferences: UserPreferencesUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """更新用户偏好设置"""
    try:
        updated_user = user.update_preferences(
            db=db, user_id=current_user.id, preferences=preferences
        )
        
        return StandardJSONResponse(
            content={
                "preferences": updated_user.preferences
            },
            message="偏好设置更新成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"更新偏好设置失败: {str(e)}"
        )


@router.post("/me/change-password", tags=["用户管理"])
def change_user_password(
    *,
    db: Session = Depends(get_db),
    password_data: PasswordChange,
    current_user: UserResponse = Depends(get_current_user)
):
    """修改用户密码"""
    try:
        # 验证新密码确认
        if password_data.new_password != password_data.confirm_password:
            return StandardJSONResponse(
                content=None,
                status_code=400,
                message="新密码与确认密码不匹配"
            )
        
        # 修改密码
        success = user.change_password(
            db=db,
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        if not success:
            return StandardJSONResponse(
                content=None,
                status_code=400,
                message="当前密码错误"
            )
        
        return StandardJSONResponse(
            content=None,
            message="密码修改成功，请重新登录"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"修改密码失败: {str(e)}"
        )


# ===== 向后兼容的路径别名 =====
# 注意：建议前端统一使用标准RESTful路径
@router.put("/profile", tags=["用户管理"])
def update_user_profile(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """更新用户资料（推荐使用此路径）"""
    try:
        updated_user = user.update(db=db, db_obj=current_user, obj_in=user_in)
        
        user_data = {
            "id": str(updated_user.id),
            "username": updated_user.username,
            "email": updated_user.email,
            "full_name": updated_user.full_name,
            "avatar_url": updated_user.avatar_url,
            "bio": updated_user.bio
        }
        
        return StandardJSONResponse(
            content=user_data,
            message="用户资料更新成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"更新用户资料失败: {str(e)}"
        )


@router.put("/password", tags=["用户管理"])
def change_password(
    *,
    db: Session = Depends(get_db),
    password_data: PasswordChange,
    current_user: UserResponse = Depends(get_current_user)
):
    """修改密码（推荐使用此路径）"""
    try:
        # 验证新密码确认
        if password_data.new_password != password_data.confirm_password:
            return StandardJSONResponse(
                content=None,
                status_code=400,
                message="新密码与确认密码不匹配"
            )

        # 修改密码
        success = user.change_password(
            db=db,
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )

        if not success:
            return StandardJSONResponse(
                content=None,
                status_code=400,
                message="当前密码错误"
            )

        return StandardJSONResponse(
            content=None,
            message="密码修改成功，请重新登录"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"修改密码失败: {str(e)}"
        )
