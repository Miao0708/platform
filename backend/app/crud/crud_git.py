"""
Git配置相关CRUD操作
"""
from typing import Optional, List
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.git import GlobalGitCredential, Repository, GitPlatformConfig
from app.schemas.git import (
    GitCredentialCreate, GitCredentialUpdate,
    RepositoryCreate, RepositoryUpdate,
    GitPlatformConfigCreate, GitPlatformConfigUpdate
)
from app.core.security import encrypt_token, decrypt_token


class CRUDGitPlatformConfig(CRUDBase[GitPlatformConfig, GitPlatformConfigCreate, GitPlatformConfigUpdate]):
    """Git平台配置CRUD操作"""
    
    def create(self, db: Session, *, obj_in: GitPlatformConfigCreate) -> GitPlatformConfig:
        """创建Git平台配置（加密token）"""
        # 加密token
        encrypted_token = encrypt_token(obj_in.token)
        
        # 创建数据库对象
        db_obj = GitPlatformConfig(
            name=obj_in.name,
            platform=obj_in.platform,
            username=obj_in.username,
            encrypted_token=encrypted_token,
            base_url=obj_in.base_url
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: GitPlatformConfig, obj_in: GitPlatformConfigUpdate
    ) -> GitPlatformConfig:
        """更新Git平台配置"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # 如果更新token，需要加密
        if "token" in update_data:
            update_data["encrypted_token"] = encrypt_token(update_data["token"])
            del update_data["token"]
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[GitPlatformConfig]:
        """根据名称获取平台配置"""
        statement = select(GitPlatformConfig).where(GitPlatformConfig.name == name)
        return db.exec(statement).first()
    
    def get_active_configs(self, db: Session) -> List[GitPlatformConfig]:
        """获取所有激活的平台配置"""
        statement = select(GitPlatformConfig).where(GitPlatformConfig.is_active == True)
        return list(db.exec(statement).all())
    
    def get_decrypted_token(self, db: Session, config_id: int) -> Optional[str]:
        """获取解密后的token"""
        config = self.get(db, config_id)
        if config:
            return decrypt_token(config.encrypted_token)
        return None


class CRUDGitCredential(CRUDBase[GlobalGitCredential, GitCredentialCreate, GitCredentialUpdate]):
    """Git凭证CRUD操作（兼容性保留）"""
    
    def create(self, db: Session, *, obj_in: GitCredentialCreate) -> GlobalGitCredential:
        """创建Git凭证（加密token）"""
        # 加密token
        encrypted_token = encrypt_token(obj_in.token)
        
        # 创建数据库对象
        db_obj = GlobalGitCredential(
            username=obj_in.username,
            encrypted_token=encrypted_token
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: GlobalGitCredential, obj_in: GitCredentialUpdate
    ) -> GlobalGitCredential:
        """更新Git凭证"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # 如果更新token，需要加密
        if "token" in update_data:
            update_data["encrypted_token"] = encrypt_token(update_data["token"])
            del update_data["token"]
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_active_credential(self, db: Session) -> Optional[GlobalGitCredential]:
        """获取激活的Git凭证"""
        statement = select(GlobalGitCredential).where(GlobalGitCredential.is_active == True)
        return db.exec(statement).first()
    
    def get_decrypted_token(self, db: Session, credential_id: int) -> Optional[str]:
        """获取解密后的token"""
        credential = self.get(db, credential_id)
        if credential:
            return decrypt_token(credential.encrypted_token)
        return None


class CRUDRepository(CRUDBase[Repository, RepositoryCreate, RepositoryUpdate]):
    """仓库配置CRUD操作"""
    
    def get_by_alias(self, db: Session, *, alias: str) -> Optional[Repository]:
        """根据别名获取仓库"""
        statement = select(Repository).where(Repository.alias == alias)
        return db.exec(statement).first()
    
    def get_active_repositories(self, db: Session) -> List[Repository]:
        """获取所有激活的仓库"""
        statement = select(Repository).where(Repository.is_active == True)
        return list(db.exec(statement).all())
    
    def get_repositories_with_platform(self, db: Session, skip: int = 0, limit: int = 100) -> List[Repository]:
        """获取仓库列表并包含平台配置信息"""
        statement = (
            select(Repository)
            .offset(skip)
            .limit(limit)
            .order_by(Repository.created_at.desc())
        )
        repositories = list(db.exec(statement).all())
        
        # 手动加载平台配置信息
        for repo in repositories:
            if repo.platform_config_id:
                platform_config = db.get(GitPlatformConfig, repo.platform_config_id)
                if platform_config:
                    # 这里可以添加平台配置的名称到repository对象中（需要在响应中处理）
                    repo.platform_config = platform_config
        
        return repositories
    
    def create(self, db: Session, *, obj_in: RepositoryCreate) -> Repository:
        """创建仓库配置"""
        # 检查别名是否已存在
        existing = self.get_by_alias(db, alias=obj_in.alias)
        if existing:
            raise ValueError(f"仓库别名 '{obj_in.alias}' 已存在")
        
        # 检查平台配置是否存在
        if obj_in.platform_config_id:
            platform_config = db.get(GitPlatformConfig, obj_in.platform_config_id)
            if not platform_config:
                raise ValueError(f"平台配置ID {obj_in.platform_config_id} 不存在")
        
        return super().create(db, obj_in=obj_in)


# 创建CRUD实例
git_platform_config = CRUDGitPlatformConfig(GitPlatformConfig)
git_credential = CRUDGitCredential(GlobalGitCredential)
repository = CRUDRepository(Repository)
