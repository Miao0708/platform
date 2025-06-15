"""
Celery应用配置
"""
from celery import Celery
from app.core.config import settings

# 创建Celery应用
celery_app = Celery(
    "ai_dev_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.code_diff_tasks",
        "app.tasks.requirement_tasks", 
        "app.tasks.pipeline_tasks"
    ]
)

# 配置Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=[settings.CELERY_TASK_SERIALIZER],
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    task_soft_time_limit=25 * 60,  # 25分钟软超时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 任务路由配置
celery_app.conf.task_routes = {
    "app.tasks.code_diff_tasks.*": {"queue": "code_diff"},
    "app.tasks.requirement_tasks.*": {"queue": "requirement"},
    "app.tasks.pipeline_tasks.*": {"queue": "pipeline"},
}

# 定义队列
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_queues = {
    "default": {
        "exchange": "default",
        "routing_key": "default",
    },
    "code_diff": {
        "exchange": "code_diff",
        "routing_key": "code_diff",
    },
    "requirement": {
        "exchange": "requirement", 
        "routing_key": "requirement",
    },
    "pipeline": {
        "exchange": "pipeline",
        "routing_key": "pipeline",
    },
}

if __name__ == "__main__":
    celery_app.start()
