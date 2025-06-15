"""
用户CRUD操作（极简版）
"""
from typing import Optional
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserRegister, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserRegister, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        statement = select(User).where(User.username == username)
        return db.exec(statement).first()

    def create(self, db: Session, *, obj_in: UserRegister) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if self.get_by_username(db, username=obj_in.username):
            raise ValueError("用户名已存在")
        
        # 创建用户对象
        db_obj = User(
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            is_active=True,
            is_superuser=False
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """用户认证"""
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """检查用户是否激活"""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """检查用户是否是超级用户"""
        return user.is_superuser


user = CRUDUser(User)
