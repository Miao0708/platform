"""
需求文档相关CRUD操作
"""
from typing import Optional, List
from sqlmodel import Session, select, and_
from app.crud.base import CRUDBase
from app.models.requirement import RequirementDocument, RequirementAnalysisTask, RequirementTestTask
from app.schemas.requirement import (
    RequirementDocumentCreate, RequirementDocumentUpdate,
    RequirementAnalysisTaskCreate, RequirementTestTaskCreate
)


class CRUDRequirementDocument(CRUDBase[RequirementDocument, RequirementDocumentCreate, RequirementDocumentUpdate]):
    """需求文档CRUD操作"""
    
    def get_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 20) -> List[RequirementDocument]:
        """根据状态获取需求文档列表"""
        statement = select(RequirementDocument).where(
            RequirementDocument.status == status
        ).offset(skip).limit(limit).order_by(RequirementDocument.created_at.desc())
        return db.exec(statement).all()
    
    def get_multi_with_filter(
        self, 
        db: Session, 
        *, 
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> List[RequirementDocument]:
        """根据条件筛选需求文档列表"""
        statement = select(RequirementDocument)
        
        if status:
            statement = statement.where(RequirementDocument.status == status)
        
        statement = statement.offset(skip).limit(limit).order_by(RequirementDocument.created_at.desc())
        return db.exec(statement).all()
    
    def update_status(
        self, 
        db: Session, 
        *, 
        requirement_id: int, 
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[RequirementDocument]:
        """更新需求文档状态"""
        requirement = self.get(db, id=requirement_id)
        if not requirement:
            return None
            
        update_data = {"status": status}
        if error_message:
            update_data["error_message"] = error_message
            
        return self.update(db, db_obj=requirement, obj_in=update_data)
    
    def set_optimized_content(
        self, 
        db: Session, 
        *, 
        requirement_id: int, 
        optimized_content: str
    ) -> Optional[RequirementDocument]:
        """设置优化后的需求内容"""
        requirement = self.get(db, id=requirement_id)
        if not requirement:
            return None
            
        return self.update(db, db_obj=requirement, obj_in={"optimized_content": optimized_content})


class CRUDRequirementAnalysisTask(CRUDBase[RequirementAnalysisTask, RequirementAnalysisTaskCreate, dict]):
    """需求分析任务CRUD操作"""
    
    def get_by_requirement_id(self, db: Session, *, requirement_id: int) -> Optional[RequirementAnalysisTask]:
        """根据需求文档ID获取分析任务"""
        statement = select(RequirementAnalysisTask).where(
            RequirementAnalysisTask.requirement_document_id == requirement_id
        ).order_by(RequirementAnalysisTask.created_at.desc())
        return db.exec(statement).first()
    
    def get_by_status(self, db: Session, *, status: str) -> List[RequirementAnalysisTask]:
        """根据状态获取任务列表"""
        statement = select(RequirementAnalysisTask).where(
            RequirementAnalysisTask.status == status
        ).order_by(RequirementAnalysisTask.created_at.desc())
        return db.exec(statement).all()
    
    def update_status(
        self, 
        db: Session, 
        *, 
        task_id: int, 
        status: str,
        result: Optional[str] = None,
        error_message: Optional[str] = None,
        tokens_used: Optional[int] = None,
        execution_time: Optional[float] = None
    ) -> Optional[RequirementAnalysisTask]:
        """更新任务状态和结果"""
        task = self.get(db, id=task_id)
        if not task:
            return None
            
        update_data = {"status": status}
        if result:
            update_data["result"] = result
        if error_message:
            update_data["error_message"] = error_message
        if tokens_used:
            update_data["tokens_used"] = tokens_used
        if execution_time:
            update_data["execution_time"] = execution_time
            
        # 设置时间戳
        if status == "running" and not task.started_at:
            from datetime import datetime
            update_data["started_at"] = datetime.utcnow().isoformat()
        elif status in ["completed", "failed"] and not task.completed_at:
            from datetime import datetime
            update_data["completed_at"] = datetime.utcnow().isoformat()
            
        return self.update(db, db_obj=task, obj_in=update_data)


class CRUDRequirementTestTask(CRUDBase[RequirementTestTask, RequirementTestTaskCreate, dict]):
    """需求测试分析任务CRUD操作"""
    
    def get_by_status(self, db: Session, *, status: str, skip: int = 0, limit: int = 20) -> List[RequirementTestTask]:
        """根据状态获取测试任务列表"""
        statement = select(RequirementTestTask).where(
            RequirementTestTask.status == status
        ).offset(skip).limit(limit).order_by(RequirementTestTask.created_at.desc())
        return db.exec(statement).all()
    
    def get_multi_with_filter(
        self, 
        db: Session, 
        *, 
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 20
    ) -> List[RequirementTestTask]:
        """根据条件筛选测试任务列表"""
        statement = select(RequirementTestTask)
        
        if status:
            statement = statement.where(RequirementTestTask.status == status)
        
        statement = statement.offset(skip).limit(limit).order_by(RequirementTestTask.created_at.desc())
        return db.exec(statement).all()
    
    def update_status(
        self, 
        db: Session, 
        *, 
        task_id: int, 
        status: str,
        result: Optional[dict] = None,
        error_message: Optional[str] = None,
        tokens_used: Optional[int] = None,
        execution_time: Optional[float] = None
    ) -> Optional[RequirementTestTask]:
        """更新测试任务状态和结果"""
        task = self.get(db, id=task_id)
        if not task:
            return None
            
        update_data = {"status": status}
        if result:
            update_data["result"] = result
        if error_message:
            update_data["error_message"] = error_message
        if tokens_used:
            update_data["tokens_used"] = tokens_used
        if execution_time:
            update_data["execution_time"] = execution_time
            
        # 设置时间戳
        if status == "running" and not task.started_at:
            from datetime import datetime
            update_data["started_at"] = datetime.utcnow().isoformat()
        elif status in ["completed", "failed"] and not task.completed_at:
            from datetime import datetime
            update_data["completed_at"] = datetime.utcnow().isoformat()
            
        return self.update(db, db_obj=task, obj_in=update_data)


# 创建CRUD实例
requirement_document = CRUDRequirementDocument(RequirementDocument)
requirement_analysis_task = CRUDRequirementAnalysisTask(RequirementAnalysisTask)
requirement_test_task = CRUDRequirementTestTask(RequirementTestTask) 