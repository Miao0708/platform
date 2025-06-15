"""
FastAPI应用主入口 
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from app.core.config import settings
from app.core.database import create_db_and_tables, engine
from app.api.v1.api import api_router
from app.crud.crud_user import user
from app.schemas.user import UserRegister
from app.core.logging import DetailedLoggingMiddleware, setup_logging, logger


def init_admin_user():
    """初始化管理员用户"""
    with Session(engine) as db:
        # 检查是否已存在admin用户
        admin_user = user.get_by_username(db, username="admin")
        if not admin_user:
            try:
                # 创建admin用户
                admin_data = UserRegister(
                    username="admin",
                    password="admin123456"  # 生产环境应使用更强密码
                )
                admin_user = user.create(db=db, obj_in=admin_data)
                
                # 设置为超级用户
                admin_user.is_superuser = True
                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)
                
                print(f"✅ 管理员用户创建成功:")
                print(f"   用户名: {admin_user.username}")
                print(f"   密码: admin123456 (请及时修改)")
                print(f"   超级用户: {admin_user.is_superuser}")
                
            except Exception as e:
                print(f"❌ 创建管理员用户失败: {str(e)}")
        else:
            print(f"ℹ️  管理员用户已存在: {admin_user.username}")


def create_application() -> FastAPI:
    """创建FastAPI应用实例"""
    
    # 初始化日志系统
    setup_logging(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )
    
    # 添加详细日志中间件（根据DEBUG模式决定是否启用）
    if settings.DEBUG:
        app.add_middleware(
            DetailedLoggingMiddleware,
            enable_detailed_logging=True
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
    
    # 创建数据库表
    create_db_and_tables()
    
    # 初始化管理员用户
    init_admin_user()

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
