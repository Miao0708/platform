"""
仪表盘统计API端点（适配前端需求）
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from app.api.v1.deps import get_db
from app.models.task import CodeDiffTask, RequirementParseTask, PipelineTask as NewPipelineTask
from app.models.ai_model import AIModelConfig
from app.models.conversation import Conversation, Message
from app.schemas.ai_model import DashboardStats
from app.core.response import StandardJSONResponse

router = APIRouter()


@router.get("/stats", tags=["仪表盘"])
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取仪表盘统计数据"""
    try:
        # 任务统计
        total_code_diff_tasks = db.exec(select(func.count(CodeDiffTask.id))).first() or 0
        total_requirement_tasks = db.exec(select(func.count(RequirementParseTask.id))).first() or 0
        total_pipeline_tasks = db.exec(select(func.count(NewPipelineTask.id))).first() or 0
        total_tasks = total_code_diff_tasks + total_requirement_tasks + total_pipeline_tasks
        
        # 已完成任务
        completed_code_diff = db.exec(
            select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "completed")
        ).first() or 0
        completed_requirement = db.exec(
            select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "completed")
        ).first() or 0
        completed_pipeline = db.exec(
            select(func.count(NewPipelineTask.id)).where(NewPipelineTask.status == "completed")
        ).first() or 0
        completed_tasks = completed_code_diff + completed_requirement + completed_pipeline
        
        # 运行中任务
        running_code_diff = db.exec(
            select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "processing")
        ).first() or 0
        running_requirement = db.exec(
            select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "processing")
        ).first() or 0
        running_pipeline = db.exec(
            select(func.count(NewPipelineTask.id)).where(NewPipelineTask.status.in_(["running", "queued"]))
        ).first() or 0
        running_tasks = running_code_diff + running_requirement + running_pipeline
        
        # 失败任务
        failed_code_diff = db.exec(
            select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "failed")
        ).first() or 0
        failed_requirement = db.exec(
            select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "failed")
        ).first() or 0
        failed_pipeline = db.exec(
            select(func.count(NewPipelineTask.id)).where(NewPipelineTask.status == "failed")
        ).first() or 0
        failed_tasks = failed_code_diff + failed_requirement + failed_pipeline
        
        # Token使用统计
        total_tokens_from_models = db.exec(select(func.sum(AIModelConfig.total_tokens_used))).first() or 0
        total_tokens_from_conversations = db.exec(select(func.sum(Conversation.total_tokens))).first() or 0
        total_tokens_used = total_tokens_from_models + total_tokens_from_conversations
        
        # 最近任务（最近7天）
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_code_diff_tasks = db.exec(
            select(CodeDiffTask).where(
                CodeDiffTask.created_at >= seven_days_ago
            ).order_by(CodeDiffTask.created_at.desc()).limit(5)
        ).all()
        
        recent_requirement_tasks = db.exec(
            select(RequirementParseTask).where(
                RequirementParseTask.created_at >= seven_days_ago
            ).order_by(RequirementParseTask.created_at.desc()).limit(5)
        ).all()
        
        recent_pipeline_tasks = db.exec(
            select(NewPipelineTask).where(
                NewPipelineTask.created_at >= seven_days_ago
            ).order_by(NewPipelineTask.created_at.desc()).limit(5)
        ).all()
        
        # 构建最近任务列表
        recent_tasks = []
        
        for task in recent_code_diff_tasks:
            recent_tasks.append({
                "id": str(task.id),
                "name": task.name,
                "type": "code_diff",
                "status": task.status,
                "created_at": task.created_at.isoformat() + "Z"
            })
        
        for task in recent_requirement_tasks:
            recent_tasks.append({
                "id": str(task.id),
                "name": task.name,
                "type": "requirement_parse",
                "status": task.status,
                "created_at": task.created_at.isoformat() + "Z"
            })
        
        for task in recent_pipeline_tasks:
            recent_tasks.append({
                "id": str(task.id),
                "name": task.name,
                "type": "pipeline",
                "status": task.status,
                "created_at": task.created_at.isoformat() + "Z"
            })
        
        # 按时间排序并限制数量
        recent_tasks.sort(key=lambda x: x["created_at"], reverse=True)
        recent_tasks = recent_tasks[:10]
        
        stats_data = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "running_tasks": running_tasks,
            "failed_tasks": failed_tasks,
            "total_tokens_used": total_tokens_used,
            "recent_tasks": recent_tasks
        }
        
        return StandardJSONResponse(
            content=stats_data,
            message="获取仪表盘统计成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取仪表盘统计失败: {str(e)}"
        )


@router.get("/stats/charts", tags=["仪表盘"])
def get_dashboard_charts(db: Session = Depends(get_db)):
    """获取仪表盘图表数据"""
    try:
        # 最近7天的任务创建趋势
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        daily_stats = []
        for i in range(7):
            day = seven_days_ago + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            # 当天创建的任务数
            code_diff_count = db.exec(
                select(func.count(CodeDiffTask.id)).where(
                    CodeDiffTask.created_at >= day_start,
                    CodeDiffTask.created_at < day_end
                )
            ).first() or 0
            
            requirement_count = db.exec(
                select(func.count(RequirementParseTask.id)).where(
                    RequirementParseTask.created_at >= day_start,
                    RequirementParseTask.created_at < day_end
                )
            ).first() or 0
            
            pipeline_count = db.exec(
                select(func.count(NewPipelineTask.id)).where(
                    NewPipelineTask.created_at >= day_start,
                    NewPipelineTask.created_at < day_end
                )
            ).first() or 0
            
            daily_stats.append({
                "date": day.strftime("%Y-%m-%d"),
                "code_diff_tasks": code_diff_count,
                "requirement_tasks": requirement_count,
                "pipeline_tasks": pipeline_count,
                "total_tasks": code_diff_count + requirement_count + pipeline_count
            })
        
        # 任务状态分布
        task_status_distribution = {
            "code_diff": {
                "pending": db.exec(select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "pending")).first() or 0,
                "processing": db.exec(select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "processing")).first() or 0,
                "completed": db.exec(select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "completed")).first() or 0,
                "failed": db.exec(select(func.count(CodeDiffTask.id)).where(CodeDiffTask.status == "failed")).first() or 0
            },
            "requirement": {
                "pending": db.exec(select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "pending")).first() or 0,
                "processing": db.exec(select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "processing")).first() or 0,
                "completed": db.exec(select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "completed")).first() or 0,
                "failed": db.exec(select(func.count(RequirementParseTask.id)).where(RequirementParseTask.status == "failed")).first() or 0
            },
            "pipeline": {
                "pending": db.exec(select(func.count(NewPipelineTask.id)).where(NewPipelineTask.status == "pending")).first() or 0,
                "running": db.exec(select(func.count(NewPipelineTask.id)).where(NewPipelineTask.status.in_(["running", "queued"]))).first() or 0,
                "completed": db.exec(select(func.count(NewPipelineTask.id)).where(NewPipelineTask.status == "completed")).first() or 0,
                "failed": db.exec(select(func.count(NewPipelineTask.id)).where(NewPipelineTask.status == "failed")).first() or 0
            }
        }
        
        # AI模型使用统计
        model_usage_stats = []
        models = db.exec(select(AIModelConfig)).all()
        for model in models:
            model_usage_stats.append({
                "model_name": model.name,
                "provider": model.provider,
                "usage_count": model.usage_count,
                "total_tokens": model.total_tokens_used,
                "is_active": model.is_active
            })
        
        charts_data = {
            "daily_task_trend": daily_stats,
            "task_status_distribution": task_status_distribution,
            "model_usage_stats": model_usage_stats
        }
        
        return StandardJSONResponse(
            content=charts_data,
            message="获取图表数据成功"
        )
    except Exception as e:
        return StandardJSONResponse(
            content=None,
            status_code=500,
            message=f"获取图表数据失败: {str(e)}"
        )
