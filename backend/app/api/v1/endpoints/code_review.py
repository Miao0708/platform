"""
代码评审流水线相关API端点
"""
import os
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session
from app.api.v1.deps import get_db
from app.crud.crud_pipeline import code_diff, requirement_text
from app.crud.crud_task import pipeline_task, task_execution
from app.crud.crud_git import repository
from app.crud.crud_prompt import prompt_template
from app.crud.crud_knowledge_base import knowledge_base
from app.schemas.pipeline import (
    CodeDiffCreate, CodeDiffResponse,
    RequirementTextCreate, RequirementTextUpdate, RequirementTextResponse,
    PipelineTaskCreate, PipelineTaskUpdate, PipelineTaskResponse,
    TaskExecutionRequest, TaskExecutionResponse,
    TaskProgress, PipelineStats, CodeReviewResult
)
from app.core.git_utils import generate_diff
from app.core.config import settings

router = APIRouter()


# ===== 代码差异管理 =====
@router.post("/diffs", response_model=CodeDiffResponse)
def create_code_diff(
    *,
    db: Session = Depends(get_db),
    diff_in: CodeDiffCreate,
    background_tasks: BackgroundTasks
):
    """创建代码差异"""
    # 验证仓库存在
    repo = repository.get(db=db, id=diff_in.repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="仓库不存在"
        )
    
    try:
        # 检查是否已存在相同的差异
        existing_diff = code_diff.get_by_refs(
            db, 
            repository_id=diff_in.repository_id,
            base_ref=diff_in.base_ref,
            head_ref=diff_in.head_ref
        )
        
        if existing_diff:
            return existing_diff
        
        # 创建差异记录
        diff = code_diff.create(db=db, obj_in=diff_in)
        
        # 后台生成差异文件
        background_tasks.add_task(
            generate_diff_task,
            db_session=db,
            diff_id=diff.id,
            repository=repo
        )
        
        return diff
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建代码差异失败: {str(e)}"
        )


@router.get("/diffs", response_model=List[CodeDiffResponse])
def read_code_diffs(
    db: Session = Depends(get_db),
    repository_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取代码差异列表"""
    if repository_id:
        diffs = code_diff.get_by_repository(db, repository_id=repository_id)
    elif status_filter:
        diffs = code_diff.get_by_status(db, status=status_filter)
    else:
        diffs = code_diff.get_multi(db, skip=skip, limit=limit)
    
    return diffs


@router.get("/diffs/{diff_id}", response_model=CodeDiffResponse)
def read_code_diff(
    *,
    db: Session = Depends(get_db),
    diff_id: int
):
    """获取代码差异详情"""
    diff = code_diff.get(db=db, id=diff_id)
    if not diff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="代码差异不存在"
        )
    return diff


@router.get("/diffs/{diff_id}/content")
def read_diff_content(
    *,
    db: Session = Depends(get_db),
    diff_id: int
):
    """获取差异文件内容"""
    diff = code_diff.get(db=db, id=diff_id)
    if not diff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="代码差异不存在"
        )
    
    if not diff.diff_file_path or not os.path.exists(diff.diff_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="差异文件不存在"
        )
    
    try:
        with open(diff.diff_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "diff_id": diff_id,
            "content": content,
            "file_path": diff.diff_file_path,
            "base_ref": diff.base_ref,
            "head_ref": diff.head_ref
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"读取差异文件失败: {str(e)}"
        )


# ===== 需求文本管理 =====
@router.post("/requirements", response_model=RequirementTextResponse)
def create_requirement_text(
    *,
    db: Session = Depends(get_db),
    requirement_in: RequirementTextCreate
):
    """创建需求文本"""
    try:
        req = requirement_text.create(db=db, obj_in=requirement_in)
        return req
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建需求文本失败: {str(e)}"
        )


@router.get("/requirements", response_model=List[RequirementTextResponse])
def read_requirement_texts(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取需求文本列表"""
    if category:
        requirements = requirement_text.get_by_category(db, category=category)
    elif status_filter:
        requirements = requirement_text.get_by_status(db, status=status_filter)
    elif priority:
        requirements = requirement_text.get_by_priority(db, priority=priority)
    else:
        requirements = requirement_text.get_multi(db, skip=skip, limit=limit)
    
    return requirements


@router.get("/requirements/categories", response_model=List[str])
def read_requirement_categories(db: Session = Depends(get_db)):
    """获取所有需求分类"""
    categories = requirement_text.get_categories(db)
    return categories


@router.get("/requirements/{requirement_id}", response_model=RequirementTextResponse)
def read_requirement_text(
    *,
    db: Session = Depends(get_db),
    requirement_id: int
):
    """获取需求文本详情"""
    req = requirement_text.get(db=db, id=requirement_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="需求文本不存在"
        )
    return req


@router.put("/requirements/{requirement_id}", response_model=RequirementTextResponse)
def update_requirement_text(
    *,
    db: Session = Depends(get_db),
    requirement_id: int,
    requirement_in: RequirementTextUpdate
):
    """更新需求文本"""
    req = requirement_text.get(db=db, id=requirement_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="需求文本不存在"
        )
    
    try:
        req = requirement_text.update(db=db, db_obj=req, obj_in=requirement_in)
        return req
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新需求文本失败: {str(e)}"
        )


# ===== 流水线任务管理 =====
@router.post("/tasks", response_model=PipelineTaskResponse)
def create_pipeline_task(
    *,
    db: Session = Depends(get_db),
    task_in: PipelineTaskCreate
):
    """创建流水线任务"""
    try:
        # 验证关联资源存在
        if task_in.code_diff_id:
            diff = code_diff.get(db=db, id=task_in.code_diff_id)
            if not diff:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="代码差异不存在"
                )
        
        if task_in.requirement_text_id:
            req = requirement_text.get(db=db, id=task_in.requirement_text_id)
            if not req:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="需求文本不存在"
                )
        
        if task_in.prompt_template_id:
            template = prompt_template.get(db=db, id=task_in.prompt_template_id)
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Prompt模板不存在"
                )
        
        if task_in.knowledge_base_id:
            kb = knowledge_base.get(db=db, id=task_in.knowledge_base_id)
            if not kb:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="知识库不存在"
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


@router.get("/tasks", response_model=List[PipelineTaskResponse])
def read_pipeline_tasks(
    db: Session = Depends(get_db),
    task_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """获取流水线任务列表"""
    if task_type:
        tasks = pipeline_task.get_by_type(db, task_type=task_type)
    elif status_filter:
        tasks = pipeline_task.get_by_status(db, status=status_filter)
    else:
        tasks = pipeline_task.get_multi(db, skip=skip, limit=limit)
    
    return tasks


@router.get("/tasks/stats", response_model=PipelineStats)
def read_pipeline_stats(db: Session = Depends(get_db)):
    """获取流水线统计信息"""
    try:
        stats = pipeline_task.get_stats(db)
        return PipelineStats(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=PipelineTaskResponse)
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


@router.put("/tasks/{task_id}", response_model=PipelineTaskResponse)
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


@router.post("/tasks/{task_id}/execute", response_model=TaskExecutionResponse)
async def execute_pipeline_task(
    *,
    db: Session = Depends(get_db),
    task_id: int,
    execute_request: Optional[TaskExecutionRequest] = None,
    background_tasks: BackgroundTasks
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
            task_id=task_id,
            steps_total=5  # 代码评审的标准步骤数
        )

        # 更新任务状态
        pipeline_task.update_status(db, task_id=task_id, status="queued")

        # 后台执行任务
        background_tasks.add_task(
            execute_code_review_task,
            db_session=db,
            task_id=task_id,
            execution_id=execution.execution_id,
            config_override=execute_request.config_override if execute_request else None
        )

        return execution
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动任务执行失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/executions", response_model=List[TaskExecutionResponse])
def read_task_executions(
    *,
    db: Session = Depends(get_db),
    task_id: int
):
    """获取任务执行历史"""
    task = pipeline_task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="流水线任务不存在"
        )

    executions = task_execution.get_by_task(db, task_id=task_id)
    return executions


@router.get("/executions/{execution_id}/progress", response_model=TaskProgress)
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

    # 计算进度百分比
    progress = 0.0
    if execution.steps_total > 0:
        progress = (execution.steps_completed / execution.steps_total) * 100

    # 估算剩余时间（简单实现）
    estimated_remaining_time = None
    if execution.status == "running" and execution.steps_completed > 0:
        # 基于已完成步骤估算
        avg_time_per_step = 30  # 假设每步30秒
        remaining_steps = execution.steps_total - execution.steps_completed
        estimated_remaining_time = remaining_steps * avg_time_per_step

    return TaskProgress(
        task_id=execution.task_id,
        execution_id=execution.execution_id,
        status=execution.status,
        progress=progress,
        current_step=execution.current_step or "准备中",
        steps_completed=execution.steps_completed,
        steps_total=execution.steps_total,
        estimated_remaining_time=estimated_remaining_time
    )


# ===== 后台任务函数 =====
def generate_diff_task(db_session: Session, diff_id: int, repository):
    """后台生成差异文件任务"""
    try:
        # 更新状态为生成中
        code_diff.update_status(db_session, diff_id=diff_id, status="generating")

        # 生成差异文件路径
        diff_dir = os.path.join(settings.UPLOAD_DIR, "diffs")
        os.makedirs(diff_dir, exist_ok=True)

        diff_obj = code_diff.get(db_session, diff_id)
        output_path = os.path.join(
            diff_dir,
            f"diff_{diff_id}_{diff_obj.base_ref}_{diff_obj.head_ref}.diff"
        )

        # 生成差异
        success, message = generate_diff(
            repository.url,
            repository.username,
            repository.password,
            diff_obj.base_ref,
            diff_obj.head_ref,
            output_path
        )

        if success:
            code_diff.update_status(
                db_session,
                diff_id=diff_id,
                status="completed",
                diff_file_path=output_path
            )
        else:
            code_diff.update_status(
                db_session,
                diff_id=diff_id,
                status="failed",
                error_message=message
            )
    except Exception as e:
        code_diff.update_status(
            db_session,
            diff_id=diff_id,
            status="failed",
            error_message=str(e)
        )


async def execute_code_review_task(
    db_session: Session,
    task_id: int,
    execution_id: str,
    config_override: dict = None
):
    """执行代码评审任务"""
    try:
        # 更新执行状态
        task_execution.update_progress(
            db_session,
            execution_id=execution_id,
            steps_completed=0,
            current_step="初始化任务"
        )

        # 获取任务信息
        task = pipeline_task.get(db_session, task_id)
        if not task:
            raise Exception("任务不存在")

        # 步骤1: 读取代码差异
        task_execution.update_progress(
            db_session,
            execution_id=execution_id,
            steps_completed=1,
            current_step="读取代码差异"
        )

        diff_content = ""
        if task.code_diff_id:
            diff_obj = code_diff.get(db_session, task.code_diff_id)
            if diff_obj and diff_obj.diff_file_path and os.path.exists(diff_obj.diff_file_path):
                with open(diff_obj.diff_file_path, 'r', encoding='utf-8') as f:
                    diff_content = f.read()

        # 步骤2: 读取需求文本
        task_execution.update_progress(
            db_session,
            execution_id=execution_id,
            steps_completed=2,
            current_step="读取需求文本"
        )

        requirement_content = ""
        if task.requirement_text_id:
            req_obj = requirement_text.get(db_session, task.requirement_text_id)
            if req_obj:
                requirement_content = req_obj.refined_content or req_obj.original_content

        # 步骤3: 获取知识库上下文（如果需要）
        task_execution.update_progress(
            db_session,
            execution_id=execution_id,
            steps_completed=3,
            current_step="获取知识库上下文"
        )

        knowledge_context = ""
        if task.knowledge_base_id and diff_content:
            try:
                from app.services.rag_service import rag_service
                context, _ = rag_service.get_context_for_query(
                    db_session,
                    query=diff_content[:1000],  # 使用差异内容的前1000字符作为查询
                    knowledge_base_id=task.knowledge_base_id,
                    max_context_length=2000
                )
                knowledge_context = context
            except Exception as e:
                print(f"获取知识库上下文失败: {e}")

        # 步骤4: 解析Prompt模板
        task_execution.update_progress(
            db_session,
            execution_id=execution_id,
            steps_completed=4,
            current_step="解析Prompt模板"
        )

        final_prompt = ""
        if task.prompt_template_id:
            template = prompt_template.get(db_session, task.prompt_template_id)
            if template:
                from app.services.prompt_service import prompt_service

                variables = {
                    "code_diff": diff_content,
                    "requirement_text": requirement_content,
                    "knowledge_context": knowledge_context
                }

                final_prompt = await prompt_service.resolve_prompt_content(
                    db_session, template.content, variables
                )

        # 步骤5: 生成评审结果（模拟LLM调用）
        task_execution.update_progress(
            db_session,
            execution_id=execution_id,
            steps_completed=5,
            current_step="生成评审结果"
        )

        # TODO: 这里应该调用实际的LLM API
        # 目前使用模拟结果
        review_result = {
            "summary": "代码评审完成，发现若干需要关注的问题",
            "issues": [
                {
                    "type": "security",
                    "severity": "medium",
                    "description": "建议加强输入验证",
                    "suggestion": "添加参数校验逻辑"
                }
            ],
            "suggestions": [
                "增加单元测试覆盖率",
                "优化代码结构"
            ],
            "security_score": 80,
            "quality_score": 85
        }

        result_text = f"代码评审结果:\n{str(review_result)}"

        # 完成任务
        execution_time = time.time() - time.time()  # 实际应该记录开始时间

        task_execution.complete_execution(
            db_session,
            execution_id=execution_id,
            status="completed",
            result=result_text,
            resources_used={
                "llm_tokens": 2500,
                "processing_time": execution_time
            }
        )

        pipeline_task.update_status(
            db_session,
            task_id=task_id,
            status="completed",
            result=result_text,
            execution_time=execution_time
        )

    except Exception as e:
        # 任务失败
        task_execution.complete_execution(
            db_session,
            execution_id=execution_id,
            status="failed",
            error_message=str(e)
        )

        pipeline_task.update_status(
            db_session,
            task_id=task_id,
            status="failed",
            error_message=str(e)
        )
