"""
FastAPI应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api.v1.api import api_router


def create_application() -> FastAPI:
    """创建FastAPI应用实例"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )
    
    # 添加CORS中间件
    # 根据环境配置允许的域名
    allowed_origins = settings.allowed_origins_list if not settings.DEBUG else ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # 添加请求日志中间件（开发环境）
    if settings.DEBUG:
        @app.middleware("http")
        async def log_requests(request, call_next):
            import time
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            print(f"[{request.client.host}] {request.method} {request.url} - {response.status_code} ({process_time:.3f}s)")
            return response
    
    # 创建数据库表
    create_db_and_tables()

    # 包含API路由
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


# 创建应用实例
app = create_application()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI研发辅助平台后端API",
        "version": settings.VERSION,
        "docs_url": f"{settings.API_V1_STR}/docs",
        "debug": settings.DEBUG
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": settings.VERSION}
