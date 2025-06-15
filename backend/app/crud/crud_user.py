"""
用户相关CRUD操作
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from app.crud.base import CRUDBase
from app.models.user import User, UserSession, UserLoginLog
from app.schemas.user import UserRegister, UserUpdate, UserPreferencesUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserRegister, UserUpdate]):
    """用户CRUD操作"""
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        return db.exec(statement).first()
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        statement = select(User).where(User.email == email)
        return db.exec(statement).first()
    
    def get_by_username_or_email(self, db: Session, *, identifier: str) -> Optional[User]:
        """根据用户名或邮箱获取用户"""
        statement = select(User).where(
            (User.username == identifier) | (User.email == identifier)
        )
        return db.exec(statement).first()
    
    def create(self, db: Session, *, obj_in: UserRegister) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing_user = self.get_by_username(db, username=obj_in.username)
        if existing_user:
            raise ValueError(f"用户名 '{obj_in.username}' 已存在")
        
        # 检查邮箱是否已存在
        existing_email = self.get_by_email(db, email=obj_in.email)
        if existing_email:
            raise ValueError(f"邮箱 '{obj_in.email}' 已存在")
        
        # 创建用户
        user_data = obj_in.model_dump()
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """验证用户登录"""
        user = self.get_by_username_or_email(db, identifier=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def update_login_info(self, db: Session, *, user_id: int) -> User:
        """更新用户登录信息"""
        user = self.get(db, user_id)
        if user:
            user.login_count += 1
            user.last_login_at = datetime.utcnow().isoformat()
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    def update_preferences(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        preferences: UserPreferencesUpdate
    ) -> User:
        """更新用户偏好设置"""
        user = self.get(db, user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 合并偏好设置
        current_prefs = user.preferences or {}
        new_prefs = preferences.model_dump(exclude_unset=True)
        
        # 深度合并字典
        for key, value in new_prefs.items():
            if isinstance(value, dict) and key in current_prefs:
                current_prefs[key].update(value)
            else:
                current_prefs[key] = value
        
        user.preferences = current_prefs
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def change_password(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """修改用户密码"""
        user = self.get(db, user_id)
        if not user:
            return False
        
        # 验证当前密码
        if not verify_password(current_password, user.hashed_password):
            return False
        
        # 更新密码
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        db.commit()
        return True
    
    def get_active_users(self, db: Session) -> List[User]:
        """获取所有活跃用户"""
        statement = select(User).where(User.is_active == True)
        return db.exec(statement).all()
    
    def get_stats(self, db: Session) -> Dict[str, int]:
        """获取用户统计信息"""
        # 总用户数
        total_users = db.exec(select(func.count(User.id))).first()
        
        # 活跃用户数
        active_users = db.exec(
            select(func.count(User.id)).where(User.is_active == True)
        ).first()
        
        # 已验证用户数
        verified_users = db.exec(
            select(func.count(User.id)).where(User.is_verified == True)
        ).first()
        
        # 今日新增用户
        today = datetime.utcnow().date()
        new_users_today = db.exec(
            select(func.count(User.id)).where(
                func.date(User.created_at) == today
            )
        ).first()
        
        # 当前登录会话数
        login_sessions = db.exec(
            select(func.count(UserSession.id)).where(
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow().isoformat()
            )
        ).first()
        
        return {
            "total_users": total_users or 0,
            "active_users": active_users or 0,
            "verified_users": verified_users or 0,
            "new_users_today": new_users_today or 0,
            "login_sessions": login_sessions or 0
        }


class CRUDUserSession(CRUDBase[UserSession, dict, dict]):
    """用户会话CRUD操作"""
    
    def create_session(
        self, 
        db: Session, 
        *, 
        user_id: int,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        device_info: str = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> UserSession:
        """创建用户会话"""
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        session = UserSession(
            user_id=user_id,
            session_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at.isoformat(),
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    def get_by_token(self, db: Session, *, token: str) -> Optional[UserSession]:
        """根据会话令牌获取会话"""
        statement = select(UserSession).where(
            UserSession.session_token == token,
            UserSession.is_active == True
        )
        return db.exec(statement).first()
    
    def get_by_refresh_token(self, db: Session, *, refresh_token: str) -> Optional[UserSession]:
        """根据刷新令牌获取会话"""
        statement = select(UserSession).where(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True
        )
        return db.exec(statement).first()
    
    def get_user_sessions(self, db: Session, *, user_id: int) -> List[UserSession]:
        """获取用户的所有活跃会话"""
        statement = select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow().isoformat()
        )
        return db.exec(statement).all()
    
    def revoke_session(self, db: Session, *, session_id: int) -> bool:
        """撤销会话"""
        session = self.get(db, session_id)
        if session:
            session.is_active = False
            db.add(session)
            db.commit()
            return True
        return False
    
    def revoke_user_sessions(self, db: Session, *, user_id: int) -> int:
        """撤销用户的所有会话"""
        sessions = self.get_user_sessions(db, user_id=user_id)
        count = 0
        for session in sessions:
            session.is_active = False
            db.add(session)
            count += 1
        db.commit()
        return count


class CRUDUserLoginLog(CRUDBase[UserLoginLog, dict, dict]):
    """用户登录日志CRUD操作"""
    
    def create_log(
        self,
        db: Session,
        *,
        user_id: int,
        login_type: str,
        success: bool,
        ip_address: str = None,
        user_agent: str = None,
        device_info: str = None,
        location: str = None,
        failure_reason: str = None
    ) -> UserLoginLog:
        """创建登录日志"""
        log = UserLoginLog(
            user_id=user_id,
            login_type=login_type,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            location=location,
            failure_reason=failure_reason
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    def get_user_logs(
        self, 
        db: Session, 
        *, 
        user_id: int, 
        limit: int = 50
    ) -> List[UserLoginLog]:
        """获取用户登录日志"""
        statement = select(UserLoginLog).where(
            UserLoginLog.user_id == user_id
        ).order_by(UserLoginLog.created_at.desc()).limit(limit)
        return db.exec(statement).all()


# 创建CRUD实例
user = CRUDUser(User)
user_session = CRUDUserSession(UserSession)
user_login_log = CRUDUserLoginLog(UserLoginLog)
