"""
流水线相关CRUD操作
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select, func
from app.crud.base import CRUDBase
from app.models.pipeline import CodeDiff, RequirementText
from app.schemas.pipeline import (
    CodeDiffCreate, RequirementTextCreate, RequirementTextUpdate
)


class CRUDCodeDiff(CRUDBase[CodeDiff, CodeDiffCreate, dict]):
    """代码差异CRUD操作"""
    
    def get_by_repository(self, db: Session, *, repository_id: int) -> List[CodeDiff]:
        """获取仓库的所有代码差异"""
        statement = select(CodeDiff).where(CodeDiff.repository_id == repository_id)
        return db.exec(statement).all()
    
    def get_by_status(self, db: Session, *, status: str) -> List[CodeDiff]:
        """根据状态获取代码差异"""
        statement = select(CodeDiff).where(CodeDiff.status == status)
        return db.exec(statement).all()
    
    def update_status(
        self, 
        db: Session, 
        *, 
        diff_id: int, 
        status: str, 
        diff_file_path: str = None,
        error_message: str = None
    ) -> Optional[CodeDiff]:
        """更新代码差异状态"""
        diff = self.get(db, diff_id)
        if diff:
            diff.status = status
            if diff_file_path:
                diff.diff_file_path = diff_file_path
            if error_message:
                diff.error_message = error_message
            db.add(diff)
            db.commit()
            db.refresh(diff)
        return diff
    
    def get_by_refs(
        self, 
        db: Session, 
        *, 
        repository_id: int, 
        base_ref: str, 
        head_ref: str
    ) -> Optional[CodeDiff]:
        """根据仓库和分支获取代码差异"""
        statement = select(CodeDiff).where(
            CodeDiff.repository_id == repository_id,
            CodeDiff.base_ref == base_ref,
            CodeDiff.head_ref == head_ref
        )
        return db.exec(statement).first()


class CRUDRequirementText(CRUDBase[RequirementText, RequirementTextCreate, RequirementTextUpdate]):
    """需求文本CRUD操作"""
    
    def get_by_category(self, db: Session, *, category: str) -> List[RequirementText]:
        """根据分类获取需求文本"""
        statement = select(RequirementText).where(RequirementText.category == category)
        return db.exec(statement).all()
    
    def get_by_status(self, db: Session, *, status: str) -> List[RequirementText]:
        """根据状态获取需求文本"""
        statement = select(RequirementText).where(RequirementText.status == status)
        return db.exec(statement).all()
    
    def get_by_priority(self, db: Session, *, priority: str) -> List[RequirementText]:
        """根据优先级获取需求文本"""
        statement = select(RequirementText).where(RequirementText.priority == priority)
        return db.exec(statement).all()
    
    def search_by_title(self, db: Session, *, title_query: str) -> List[RequirementText]:
        """根据标题搜索需求文本"""
        statement = select(RequirementText).where(
            RequirementText.title.contains(title_query)
        )
        return db.exec(statement).all()
    
    def get_categories(self, db: Session) -> List[str]:
        """获取所有分类"""
        statement = select(RequirementText.category).distinct()
        results = db.exec(statement).all()
        return [c for c in results if c is not None]


# PipelineTask CRUD操作已移动到 app/crud/crud_task.py 中


# TaskExecution CRUD操作已移动到 app/crud/crud_task.py 中


# 创建CRUD实例
code_diff = CRUDCodeDiff(CodeDiff)
requirement_text = CRUDRequirementText(RequirementText)
