"""
三级分离的任务管理API端点
"""
import os
import json
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_task import code_diff_task, requirement_parse_task, pipeline_task, task_execution
from app.crud.crud_git import repository
from app.schemas.task import (
    CodeDiffTaskCreate, CodeDiffTaskResponse, CodeDiffTaskUpdate, CodeDiffTaskSelector,
    RequirementParseTaskCreate, RequirementParseTaskResponse, RequirementParseTaskUpdate,
    RequirementParseTaskFileUpload, RequirementTaskSelector,
    PipelineTaskCreate, PipelineTaskResponse, PipelineTaskUpdate,
    TaskExecutionResponse, TaskExecutionRequest, TaskStats
)
from app.core.config import settings
from app.tasks.requirement_tasks import parse_requirement_text, process_requirement_file

router = APIRouter()


# ===== 代码差异任务管理 =====
@router.post("/code-diff", response_model=CodeDiffTaskResponse, tags=["代码差异任务"])
def create_code_diff_task(
    *,
    db: Session = Depends(get_db),
    task_in: CodeDiffTaskCreate,
    background_tasks: BackgroundTasks
):
    """创建代码差异任务"""
    # 验证仓库存在
    repo = repository.get(db=db, id=task_in.repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库不存在"
        )
    
    try:
        # 检查是否已存在相同的差异任务
        existing_task = code_diff_task.get_by_refs(
            db, 
            repository_id=task_in.repository_id,
            base_ref=task_in.base_ref,
            head_ref=task_in.head_ref
        )
        
        if existing_task:
            return existing_task
        
        # 创建任务
        task = code_diff_task.create(db=db, obj_in=task_in)
        
        # 后台生成差异
        background_tasks.add_task(
            generate_code_diff_task,
            task_id=task.id,
            repository=repo
        )
        
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建代码差异任务失败: {str(e)}"
        )


@router.get("/code-diff", response_model=List[CodeDiffTaskResponse], tags=["代码差异任务"])
def read_code_diff_tasks(
    db: Session = Depends(get_db),
    repository_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取代码差异任务列表"""
    if repository_id:
        tasks = code_diff_task.get_by_repository(db, repository_id=repository_id)
    elif status_filter:
        tasks = code_diff_task.get_by_status(db, status=status_filter)
    else:
        tasks = code_diff_task.get_multi(db, skip=skip, limit=limit)
    
    return tasks


@router.get("/code-diff/selectors", response_model=List[CodeDiffTaskSelector], tags=["代码差异任务"])
def read_code_diff_selectors(db: Session = Depends(get_db)):
    """获取已完成的代码差异任务（用于流水线选择）"""
    tasks = code_diff_task.get_completed_tasks(db)
    return [
        CodeDiffTaskSelector(
            id=task.id,
            name=task.name,
            status=task.status,
            created_at=task.created_at,
            repository_id=task.repository_id,
            base_ref=task.base_ref,
            head_ref=task.head_ref,
            files_changed=task.files_changed,
            lines_added=task.lines_added,
            lines_deleted=task.lines_deleted
        )
        for task in tasks
    ]


@router.get("/code-diff/{task_id}", response_model=CodeDiffTaskResponse, tags=["代码差异任务"])
def read_code_diff_task(
    *,
    db: Session = Depends(get_db),
    task_id: int
):
    """获取代码差异任务详情"""
    task = code_diff_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="代码差异任务不存在"
        )
    return task


@router.put("/code-diff/{task_id}", response_model=CodeDiffTaskResponse, tags=["代码差异任务"])
def update_code_diff_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    task_in: CodeDiffTaskUpdate
):
    """更新代码差异任务"""
    task = code_diff_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="代码差异任务不存在"
        )
    
    try:
        task = code_diff_task.update(db=db, db_obj=task, obj_in=task_in)
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新代码差异任务失败: {str(e)}"
        )


@router.get("/code-diff/{task_id}/content", tags=["代码差异任务"])
def read_code_diff_content(
    *,
    db: Session = Depends(get_db),
    task_id: int
):
    """获取代码差异内容"""
    task = code_diff_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="代码差异任务不存在"
        )
    
    if not task.diff_file_path or not os.path.exists(task.diff_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="差异文件不存在"
        )
    
    try:
        with open(task.diff_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "task_id": task_id,
            "content": content,
            "file_path": task.diff_file_path,
            "summary": task.diff_summary,
            "stats": {
                "files_changed": task.files_changed,
                "lines_added": task.lines_added,
                "lines_deleted": task.lines_deleted
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"读取差异文件失败: {str(e)}"
        )


# ===== 需求解析任务管理 =====
@router.post("/requirements", response_model=RequirementParseTaskResponse, tags=["需求解析任务"])
def create_requirement_task(
    *,
    db: Session = Depends(get_db),
    task_in: RequirementParseTaskCreate
):
    """创建需求解析任务（文本输入）"""
    try:
        task = requirement_parse_task.create(db=db, obj_in=task_in)
        
        # 如果有文本内容，立即启动解析任务
        if task.original_content and task.original_content.strip():
            parse_requirement_text.delay(task.id)
        
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建需求解析任务失败: {str(e)}"
        )


# 注意：需求文件上传接口已移至 /requirements/upload 路径
# 此处的重复实现已移除，避免路径冲突


@router.get("/requirements", response_model=List[RequirementParseTaskResponse], tags=["需求解析任务"])
def read_requirement_tasks(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取需求解析任务列表"""
    if category:
        tasks = requirement_parse_task.get_by_category(db, category=category)
    elif status_filter:
        tasks = requirement_parse_task.get_by_status(db, status=status_filter)
    elif priority:
        tasks = requirement_parse_task.get_by_priority(db, priority=priority)
    else:
        tasks = requirement_parse_task.get_multi(db, skip=skip, limit=limit)
    
    return tasks


@router.get("/requirements/selectors", response_model=List[RequirementTaskSelector], tags=["需求解析任务"])
def read_requirement_selectors(db: Session = Depends(get_db)):
    """获取已完成的需求解析任务（用于流水线选择）"""
    tasks = requirement_parse_task.get_completed_tasks(db)
    return [
        RequirementTaskSelector(
            id=task.id,
            name=task.name,
            status=task.status,
            created_at=task.created_at,
            category=task.category,
            priority=task.priority,
            complexity=task.complexity,
            estimated_hours=task.estimated_hours
        )
        for task in tasks
    ]


# ===== 后台任务函数 =====
def generate_code_diff_task(task_id: int, repository):
    """生成代码差异的后台任务"""
    from app.core.git_utils import generate_diff
    import time
    
    db = next(get_db())
    
    try:
        # 更新状态为处理中
        code_diff_task.update_status(db, task_id=task_id, status="processing")
        
        # 生成差异文件路径
        diff_dir = os.path.join(settings.UPLOAD_DIR, "diffs")
        os.makedirs(diff_dir, exist_ok=True)
        
        task = code_diff_task.get(db, task_id)
        output_path = os.path.join(
            diff_dir, 
            f"diff_{task_id}_{task.base_ref}_{task.head_ref}.diff"
        )
        
        # 生成差异
        success, message = generate_diff(
            repository.url,
            repository.username,
            repository.password,
            task.base_ref,
            task.head_ref,
            output_path
        )
        
        if success:
            # 分析差异文件
            stats = analyze_diff_file(output_path)
            
            code_diff_task.update_status(
                db, 
                task_id=task_id, 
                status="completed",
                diff_file_path=output_path,
                diff_summary=f"变更了{stats['files_changed']}个文件，新增{stats['lines_added']}行，删除{stats['lines_deleted']}行",
                files_changed=stats['files_changed'],
                lines_added=stats['lines_added'],
                lines_deleted=stats['lines_deleted']
            )
        else:
            code_diff_task.update_status(
                db, 
                task_id=task_id, 
                status="failed",
                error_message=message
            )
    except Exception as e:
        code_diff_task.update_status(
            db, 
            task_id=task_id, 
            status="failed",
            error_message=str(e)
        )
    finally:
        db.close()


def analyze_diff_file(file_path: str) -> dict:
    """分析差异文件统计信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        files_changed = 0
        lines_added = 0
        lines_deleted = 0
        
        for line in lines:
            if line.startswith('diff --git'):
                files_changed += 1
            elif line.startswith('+') and not line.startswith('+++'):
                lines_added += 1
            elif line.startswith('-') and not line.startswith('---'):
                lines_deleted += 1
        
        return {
            'files_changed': files_changed,
            'lines_added': lines_added,
            'lines_deleted': lines_deleted
        }
    except Exception:
        return {
            'files_changed': 0,
            'lines_added': 0,
            'lines_deleted': 0
        }


# ===== 流水线任务管理 =====
@router.post("/pipelines", response_model=PipelineTaskResponse, tags=["流水线任务"])
def create_pipeline_task(
    *,
    db: Session = Depends(get_db),
    task_in: PipelineTaskCreate
):
    """创建流水线任务"""
    try:
        # 验证关联的任务存在
        if task_in.code_diff_task_id:
            code_task = code_diff_task.get(db=db, id=task_in.code_diff_task_id)
            if not code_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="代码差异任务不存在"
                )
            if code_task.status != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="代码差异任务尚未完成"
                )

        if task_in.requirement_task_id:
            req_task = requirement_parse_task.get(db=db, id=task_in.requirement_task_id)
            if not req_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="需求解析任务不存在"
                )
            if req_task.status != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="需求解析任务尚未完成"
                )

        # 验证至少有一个输入
        if not task_in.code_diff_task_id and not task_in.requirement_task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="至少需要选择一个代码差异任务或需求解析任务"
            )

        task = pipeline_task.create(db=db, obj_in=task_in)
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建流水线任务失败: {str(e)}"
        )


@router.get("/pipelines", response_model=List[PipelineTaskResponse], tags=["流水线任务"])
def read_pipeline_tasks(
    db: Session = Depends(get_db),
    pipeline_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取流水线任务列表"""
    if pipeline_type:
        tasks = pipeline_task.get_by_type(db, pipeline_type=pipeline_type)
    elif status_filter:
        tasks = pipeline_task.get_by_status(db, status=status_filter)
    else:
        tasks = pipeline_task.get_multi(db, skip=skip, limit=limit)

    return tasks


@router.get("/pipelines/{task_id}", response_model=PipelineTaskResponse, tags=["流水线任务"])
def read_pipeline_task(
    *,
    db: Session = Depends(get_db),
    task_id: int
):
    """获取流水线任务详情"""
    task = pipeline_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="流水线任务不存在"
        )
    return task


@router.put("/pipelines/{task_id}", response_model=PipelineTaskResponse, tags=["流水线任务"])
def update_pipeline_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    task_in: PipelineTaskUpdate
):
    """更新流水线任务"""
    task = pipeline_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="流水线任务不存在"
        )

    try:
        task = pipeline_task.update(db=db, db_obj=task, obj_in=task_in)
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新流水线任务失败: {str(e)}"
        )


@router.post("/pipelines/{task_id}/execute", response_model=TaskExecutionResponse, tags=["流水线任务"])
def execute_pipeline_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    execute_request: Optional[TaskExecutionRequest] = None
):
    """执行流水线任务"""
    task = pipeline_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="流水线任务不存在"
        )

    if task.status in ["running", "queued"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务正在执行中"
        )

    try:
        # 创建执行记录
        execution = task_execution.create_execution(
            db=db,
            task_type="pipeline",
            task_id=task_id,
            steps_total=5
        )

        # 更新任务状态
        pipeline_task.update_status(
            db, task_id=task_id,
            status="queued",
            started_at=execution.started_at
        )

        # 启动流水线执行任务
        from app.tasks.pipeline_tasks import execute_pipeline
        config_override = execute_request.config_override if execute_request else None
        execute_pipeline.delay(task_id, config_override)

        return execution
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动流水线执行失败: {str(e)}"
        )


# ===== 任务执行管理 =====
@router.get("/executions/{execution_id}", response_model=TaskExecutionResponse, tags=["任务执行"])
def read_task_execution(
    *,
    db: Session = Depends(get_db),
    execution_id: str
):
    """获取任务执行详情"""
    execution = task_execution.get_by_execution_id(db, execution_id=execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务执行不存在"
        )
    return execution


@router.get("/executions/{execution_id}/progress", tags=["任务执行"])
def read_execution_progress(
    *,
    db: Session = Depends(get_db),
    execution_id: str
):
    """获取任务执行进度"""
    execution = task_execution.get_by_execution_id(db, execution_id=execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务执行不存在"
        )

    # 估算剩余时间
    estimated_remaining_time = None
    if execution.status == "running" and execution.steps_completed > 0:
        avg_time_per_step = 30  # 假设每步30秒
        remaining_steps = execution.steps_total - execution.steps_completed
        estimated_remaining_time = remaining_steps * avg_time_per_step

    return {
        "execution_id": execution.execution_id,
        "task_type": execution.task_type,
        "task_id": execution.task_id,
        "status": execution.status,
        "progress_percentage": execution.progress_percentage,
        "current_step": execution.current_step or "准备中",
        "steps_completed": execution.steps_completed,
        "steps_total": execution.steps_total,
        "estimated_remaining_time": estimated_remaining_time,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at
    }


# ===== 统计信息 =====
@router.get("/stats", response_model=TaskStats, tags=["统计信息"])
def read_task_stats(db: Session = Depends(get_db)):
    """获取任务统计信息"""
    try:
        code_diff_stats = code_diff_task.get_stats(db)
        requirement_stats = requirement_parse_task.get_stats(db)
        pipeline_stats = pipeline_task.get_stats(db)

        # 计算总执行次数和成功率
        total_executions = (
            code_diff_stats["completed"] + code_diff_stats["failed"] +
            requirement_stats["completed"] + requirement_stats["failed"] +
            pipeline_stats["completed"] + pipeline_stats["failed"]
        )

        total_completed = (
            code_diff_stats["completed"] +
            requirement_stats["completed"] +
            pipeline_stats["completed"]
        )

        success_rate = 0.0
        if total_executions > 0:
            success_rate = (total_completed / total_executions) * 100

        return TaskStats(
            code_diff_tasks=code_diff_stats,
            requirement_tasks=requirement_stats,
            pipeline_tasks=pipeline_stats,
            total_executions=total_executions,
            success_rate=success_rate
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )
