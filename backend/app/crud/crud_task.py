"""
任务管理相关CRUD操作（重构后的三级分离架构）
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from app.crud.base import CRUDBase
from app.models.task import CodeDiffTask, RequirementParseTask, PipelineTask, TaskExecution
from app.schemas.task import (
    CodeDiffTaskCreate, CodeDiffTaskUpdate,
    RequirementParseTaskCreate, RequirementParseTaskUpdate,
    PipelineTaskCreate, PipelineTaskUpdate
)


class CRUDCodeDiffTask(CRUDBase[CodeDiffTask, CodeDiffTaskCreate, CodeDiffTaskUpdate]):
    """代码差异任务CRUD操作"""
    
    def get_by_repository(self, db: Session, *, repository_id: int) -> List[CodeDiffTask]:
        """获取仓库的所有代码差异任务"""
        statement = select(CodeDiffTask).where(CodeDiffTask.repository_id == repository_id)
        return db.exec(statement).all()
    
    def get_by_status(self, db: Session, *, status: str) -> List[CodeDiffTask]:
        """根据状态获取代码差异任务"""
        statement = select(CodeDiffTask).where(CodeDiffTask.status == status)
        return db.exec(statement).all()
    
    def get_by_refs(
        self, 
        db: Session, 
        *, 
        repository_id: int, 
        base_ref: str, 
        head_ref: str
    ) -> Optional[CodeDiffTask]:
        """根据仓库和分支获取代码差异任务"""
        statement = select(CodeDiffTask).where(
            CodeDiffTask.repository_id == repository_id,
            CodeDiffTask.base_ref == base_ref,
            CodeDiffTask.head_ref == head_ref
        )
        return db.exec(statement).first()
    
    def update_status(
        self, 
        db: Session, 
        *, 
        task_id: int, 
        status: str,
        diff_file_path: str = None,
        diff_summary: str = None,
        files_changed: int = None,
        lines_added: int = None,
        lines_deleted: int = None,
        error_message: str = None
    ) -> Optional[CodeDiffTask]:
        """更新代码差异任务状态"""
        task = self.get(db, task_id)
        if task:
            task.status = status
            if diff_file_path:
                task.diff_file_path = diff_file_path
            if diff_summary:
                task.diff_summary = diff_summary
            if files_changed is not None:
                task.files_changed = files_changed
            if lines_added is not None:
                task.lines_added = lines_added
            if lines_deleted is not None:
                task.lines_deleted = lines_deleted
            if error_message:
                task.error_message = error_message
            db.add(task)
            db.commit()
            db.refresh(task)
        return task
    
    def get_completed_tasks(self, db: Session) -> List[CodeDiffTask]:
        """获取已完成的代码差异任务（用于流水线选择）"""
        statement = select(CodeDiffTask).where(CodeDiffTask.status == "completed")
        return db.exec(statement).all()
    
    def get_stats(self, db: Session) -> Dict[str, int]:
        """获取代码差异任务统计"""
        total = db.exec(select(func.count(CodeDiffTask.id))).first()
        pending = db.exec(select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "pending")).first()
        processing = db.exec(select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "processing")).first()
        completed = db.exec(select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "completed")).first()
        failed = db.exec(select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "failed")).first()
        
        return {
            "total": total or 0,
            "pending": pending or 0,
            "processing": processing or 0,
            "completed": completed or 0,
            "failed": failed or 0
        }


class CRUDRequirementParseTask(CRUDBase[RequirementParseTask, RequirementParseTaskCreate, RequirementParseTaskUpdate]):
    """需求解析任务CRUD操作"""
    
    def get_by_category(self, db: Session, *, category: str) -> List[RequirementParseTask]:
        """根据分类获取需求解析任务"""
        statement = select(RequirementParseTask).where(RequirementParseTask.category == category)
        return db.exec(statement).all()
    
    def get_by_status(self, db: Session, *, status: str) -> List[RequirementParseTask]:
        """根据状态获取需求解析任务"""
        statement = select(RequirementParseTask).where(RequirementParseTask.status == status)
        return db.exec(statement).all()
    
    def get_by_priority(self, db: Session, *, priority: str) -> List[RequirementParseTask]:
        """根据优先级获取需求解析任务"""
        statement = select(RequirementParseTask).where(RequirementParseTask.priority == priority)
        return db.exec(statement).all()
    
    def search_by_name(self, db: Session, *, name_query: str) -> List[RequirementParseTask]:
        """根据名称搜索需求解析任务"""
        statement = select(RequirementParseTask).where(
            RequirementParseTask.name.contains(name_query)
        )
        return db.exec(statement).all()
    
    def update_status(
        self, 
        db: Session, 
        *, 
        task_id: int, 
        status: str,
        parsed_content: str = None,
        structured_requirements: dict = None,
        category: str = None,
        complexity: str = None,
        estimated_hours: float = None,
        llm_model: str = None,
        tokens_used: int = None,
        processing_time: float = None,
        error_message: str = None
    ) -> Optional[RequirementParseTask]:
        """更新需求解析任务状态"""
        task = self.get(db, task_id)
        if task:
            task.status = status
            if parsed_content:
                task.parsed_content = parsed_content
            if structured_requirements:
                task.structured_requirements = structured_requirements
            if category:
                task.category = category
            if complexity:
                task.complexity = complexity
            if estimated_hours is not None:
                task.estimated_hours = estimated_hours
            if llm_model:
                task.llm_model = llm_model
            if tokens_used is not None:
                task.tokens_used = tokens_used
            if processing_time is not None:
                task.processing_time = processing_time
            if error_message:
                task.error_message = error_message
            db.add(task)
            db.commit()
            db.refresh(task)
        return task
    
    def get_completed_tasks(self, db: Session) -> List[RequirementParseTask]:
        """获取已完成的需求解析任务（用于流水线选择）"""
        statement = select(RequirementParseTask).where(RequirementParseTask.status == "completed")
        return db.exec(statement).all()
    
    def get_categories(self, db: Session) -> List[str]:
        """获取所有分类"""
        statement = select(RequirementParseTask.category).distinct()
        results = db.exec(statement).all()
        return [c for c in results if c is not None]
    
    def get_stats(self, db: Session) -> Dict[str, int]:
        """获取需求解析任务统计"""
        total = db.exec(select(func.count(RequirementParseTask.id))).first()
        pending = db.exec(select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "pending")).first()
        processing = db.exec(select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "processing")).first()
        completed = db.exec(select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "completed")).first()
        failed = db.exec(select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "failed")).first()
        
        return {
            "total": total or 0,
            "pending": pending or 0,
            "processing": processing or 0,
            "completed": completed or 0,
            "failed": failed or 0
        }


class CRUDPipelineTask(CRUDBase[PipelineTask, PipelineTaskCreate, PipelineTaskUpdate]):
    """流水线任务CRUD操作"""
    
    def get_by_type(self, db: Session, *, pipeline_type: str) -> List[PipelineTask]:
        """根据流水线类型获取任务"""
        statement = select(PipelineTask).where(PipelineTask.pipeline_type == pipeline_type)
        return db.exec(statement).all()
    
    def get_by_status(self, db: Session, *, status: str) -> List[PipelineTask]:
        """根据状态获取流水线任务"""
        statement = select(PipelineTask).where(PipelineTask.status == status)
        return db.exec(statement).all()
    
    def get_by_code_diff(self, db: Session, *, code_diff_task_id: int) -> List[PipelineTask]:
        """根据代码差异任务获取流水线任务"""
        statement = select(PipelineTask).where(PipelineTask.code_diff_task_id == code_diff_task_id)
        return db.exec(statement).all()
    
    def get_by_requirement(self, db: Session, *, requirement_task_id: int) -> List[PipelineTask]:
        """根据需求解析任务获取流水线任务"""
        statement = select(PipelineTask).where(PipelineTask.requirement_task_id == requirement_task_id)
        return db.exec(statement).all()
    
    def update_status(
        self, 
        db: Session, 
        *, 
        task_id: int, 
        status: str,
        result: str = None,
        result_data: dict = None,
        started_at: str = None,
        completed_at: str = None,
        execution_time: float = None,
        error_message: str = None,
        llm_model: str = None,
        tokens_used: int = None
    ) -> Optional[PipelineTask]:
        """更新流水线任务状态"""
        task = self.get(db, task_id)
        if task:
            task.status = status
            if result:
                task.result = result
            if result_data:
                task.result_data = result_data
            if started_at:
                task.started_at = started_at
            if completed_at:
                task.completed_at = completed_at
            if execution_time is not None:
                task.execution_time = execution_time
            if error_message:
                task.error_message = error_message
            if llm_model:
                task.llm_model = llm_model
            if tokens_used is not None:
                task.tokens_used = tokens_used
            db.add(task)
            db.commit()
            db.refresh(task)
        return task
    
    def get_stats(self, db: Session) -> Dict[str, int]:
        """获取流水线任务统计"""
        total = db.exec(select(func.count(PipelineTask.id))).first()
        pending = db.exec(select(func.count(PipelineTask.id)).where(PipelineTask.status == "pending")).first()
        running = db.exec(select(func.count(PipelineTask.id)).where(PipelineTask.status.in_(["queued", "running"]))).first()
        completed = db.exec(select(func.count(PipelineTask.id)).where(PipelineTask.status == "completed")).first()
        failed = db.exec(select(func.count(PipelineTask.id)).where(PipelineTask.status == "failed")).first()
        
        return {
            "total": total or 0,
            "pending": pending or 0,
            "running": running or 0,
            "completed": completed or 0,
            "failed": failed or 0
        }


class CRUDTaskExecution(CRUDBase[TaskExecution, dict, dict]):
    """任务执行CRUD操作"""
    
    def create_execution(
        self, 
        db: Session, 
        *, 
        task_type: str,
        task_id: int,
        steps_total: int = 0
    ) -> TaskExecution:
        """创建任务执行记录"""
        execution_id = f"exec_{uuid.uuid4()}"
        
        execution = TaskExecution(
            task_type=task_type,
            task_id=task_id,
            execution_id=execution_id,
            status="running",
            started_at=datetime.utcnow().isoformat(),
            steps_total=steps_total,
            steps_completed=0,
            progress_percentage=0.0
        )
        
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution
    
    def get_by_execution_id(self, db: Session, *, execution_id: str) -> Optional[TaskExecution]:
        """根据执行ID获取执行记录"""
        statement = select(TaskExecution).where(TaskExecution.execution_id == execution_id)
        return db.exec(statement).first()
    
    def get_by_task(self, db: Session, *, task_type: str, task_id: int) -> List[TaskExecution]:
        """获取任务的所有执行记录"""
        statement = select(TaskExecution).where(
            TaskExecution.task_type == task_type,
            TaskExecution.task_id == task_id
        )
        return db.exec(statement).all()
    
    def update_progress(
        self, 
        db: Session, 
        *, 
        execution_id: str,
        steps_completed: int,
        current_step: str = None,
        logs: str = None
    ) -> Optional[TaskExecution]:
        """更新执行进度"""
        execution = self.get_by_execution_id(db, execution_id=execution_id)
        if execution:
            execution.steps_completed = steps_completed
            if execution.steps_total > 0:
                execution.progress_percentage = (steps_completed / execution.steps_total) * 100
            if current_step:
                execution.current_step = current_step
            if logs:
                execution.logs = logs
            db.add(execution)
            db.commit()
            db.refresh(execution)
        return execution
    
    def complete_execution(
        self, 
        db: Session, 
        *, 
        execution_id: str,
        status: str,
        result: str = None,
        error_message: str = None,
        resources_used: dict = None
    ) -> Optional[TaskExecution]:
        """完成任务执行"""
        execution = self.get_by_execution_id(db, execution_id=execution_id)
        if execution:
            execution.status = status
            execution.completed_at = datetime.utcnow().isoformat()
            execution.progress_percentage = 100.0 if status == "completed" else execution.progress_percentage
            if result:
                execution.result = result
            if error_message:
                execution.error_message = error_message
            if resources_used:
                execution.resources_used = resources_used
            db.add(execution)
            db.commit()
            db.refresh(execution)
        return execution


# 创建CRUD实例
code_diff_task = CRUDCodeDiffTask(CodeDiffTask)
requirement_parse_task = CRUDRequirementParseTask(RequirementParseTask)
pipeline_task = CRUDPipelineTask(PipelineTask)
task_execution = CRUDTaskExecution(TaskExecution)
