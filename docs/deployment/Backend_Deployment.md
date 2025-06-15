# AI研发辅助平台 - 后端部署指南

## 🚀 部署概述

### 部署架构
```
┌─────────────────────────────────────────────────────────────┐
│                    负载均衡器 (Nginx)                        │
├─────────────────────────────────────────────────────────────┤
│  FastAPI应用 (多实例)  │  Celery Worker  │  Celery Beat     │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (主从)     │  Redis Cluster  │  ChromaDB        │
├─────────────────────────────────────────────────────────────┤
│  文件存储 (MinIO/S3)   │  日志收集       │  监控告警        │
└─────────────────────────────────────────────────────────────┘
```

### 环境要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Docker
- **Python**: 3.11+
- **PostgreSQL**: 15+
- **Redis**: 7+
- **内存**: 最小4GB，推荐8GB+
- **存储**: 最小50GB，推荐100GB+

## 🐳 Docker部署

### 1. 项目结构
```
backend/
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.celery
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   └── nginx.conf
├── scripts/
│   ├── init-db.sh
│   ├── backup-db.sh
│   └── deploy.sh
├── .env.example
└── requirements.txt
```

### 2. Dockerfile
```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libmagic1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p /app/uploads /app/logs /app/chroma_db && \
    chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Celery Dockerfile
```dockerfile
# docker/Dockerfile.celery
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN groupadd -r celeryuser && useradd -r -g celeryuser celeryuser

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p /app/logs && \
    chown -R celeryuser:celeryuser /app

# 切换到非root用户
USER celeryuser

# 启动命令（将在docker-compose中覆盖）
CMD ["celery", "-A", "app.tasks.celery_app", "worker", "--loglevel=info"]
```

### 4. Docker Compose (开发环境)
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/ai_platform
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  celery-worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.celery
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/ai_platform
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped

  celery-beat:
    build:
      context: .
      dockerfile: docker/Dockerfile.celery
    command: celery -A app.tasks.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/ai_platform
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_platform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sh:/docker-entrypoint-initdb.d/init-db.sh
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    driver: bridge
```

### 5. 生产环境 Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: ai-platform-api:latest
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@postgres:5432/ai_platform
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    volumes:
      - uploads_data:/app/uploads
      - logs_data:/app/logs
      - chroma_data:/app/chroma_db
    networks:
      - backend
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  celery-worker:
    image: ai-platform-celery:latest
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=8
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@postgres:5432/ai_platform
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
    volumes:
      - uploads_data:/app/uploads
      - logs_data:/app/logs
    networks:
      - backend

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_platform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    networks:
      - backend
    command: >
      postgres
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100

  redis:
    image: redis:7-alpine
    command: >
      redis-server
      --appendonly yes
      --maxmemory 1gb
      --maxmemory-policy allkeys-lru
      --tcp-keepalive 60
      --save 900 1
      --save 300 10
      --save 60 10000
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    networks:
      - backend

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  uploads_data:
    driver: local
  logs_data:
    driver: local
  chroma_data:
    driver: local

networks:
  backend:
    driver: overlay
    attachable: true
```

### 6. Nginx配置
```nginx
# docker/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        least_conn;
        server api:8000 max_fails=3 fail_timeout=30s;
    }

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload_limit:10m rate=1r/s;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 基础配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    server {
        listen 80;
        server_name api.yourdomain.com;

        # 重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        # SSL配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API路由
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时设置
            proxy_connect_timeout 30s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # 缓冲设置
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # 文件上传路由
        location /api/v1/upload {
            limit_req zone=upload_limit burst=5 nodelay;
            
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 上传专用超时设置
            proxy_connect_timeout 30s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
            
            client_max_body_size 50M;
        }

        # 健康检查
        location /health {
            proxy_pass http://api_backend;
            access_log off;
        }

        # 静态文件
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## 🔧 部署脚本

### 1. 初始化脚本
```bash
#!/bin/bash
# scripts/init-db.sh

set -e

echo "初始化数据库..."

# 等待PostgreSQL启动
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "等待PostgreSQL启动..."
  sleep 2
done

# 创建数据库（如果不存在）
psql -h postgres -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'ai_platform'" | grep -q 1 || psql -h postgres -U postgres -c "CREATE DATABASE ai_platform"

echo "数据库初始化完成"
```

### 2. 部署脚本
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 开始部署AI研发辅助平台后端..."

# 检查环境变量
if [ ! -f .env ]; then
    echo "❌ .env文件不存在，请先创建环境配置"
    exit 1
fi

# 加载环境变量
source .env

# 构建镜像
echo "📦 构建Docker镜像..."
docker build -t ai-platform-api:latest -f docker/Dockerfile .
docker build -t ai-platform-celery:latest -f docker/Dockerfile.celery .

# 停止旧服务
echo "🛑 停止旧服务..."
docker-compose -f docker-compose.prod.yml down

# 备份数据库
echo "💾 备份数据库..."
./scripts/backup-db.sh

# 启动新服务
echo "🔄 启动新服务..."
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 运行数据库迁移
echo "🔄 运行数据库迁移..."
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# 健康检查
echo "🔍 健康检查..."
if curl -f http://localhost/health; then
    echo "✅ 部署成功！"
else
    echo "❌ 部署失败，正在回滚..."
    docker-compose -f docker-compose.prod.yml down
    # 这里可以添加回滚逻辑
    exit 1
fi

echo "🎉 部署完成！"
```

### 3. 备份脚本
```bash
#!/bin/bash
# scripts/backup-db.sh

set -e

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="ai_platform_backup_${DATE}.sql"

echo "📦 开始备份数据库..."

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec postgres pg_dump -U postgres ai_platform > "${BACKUP_DIR}/${BACKUP_FILE}"

# 压缩备份文件
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

echo "✅ 数据库备份完成: ${BACKUP_FILE}.gz"

# 清理7天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "🧹 清理旧备份完成"
```

## 📊 监控和日志

### 1. 日志配置
```yaml
# docker-compose.yml 中的日志配置
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service,version"
```

### 2. 健康检查
```python
# app/health.py
from fastapi import APIRouter
from sqlmodel import Session, text
from app.database import get_db
from app.tasks.celery_app import celery_app
import redis
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    """综合健康检查"""
    checks = {
        "api": "healthy",
        "database": await check_database(),
        "redis": await check_redis(),
        "celery": await check_celery(),
        "timestamp": time.time()
    }
    
    # 如果任何组件不健康，返回503
    if any(status != "healthy" for status in checks.values() if status != checks["timestamp"]):
        return JSONResponse(status_code=503, content=checks)
    
    return checks

async def check_database():
    """检查数据库连接"""
    try:
        db = next(get_db())
        result = await db.execute(text("SELECT 1"))
        return "healthy"
    except Exception:
        return "unhealthy"

async def check_redis():
    """检查Redis连接"""
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        return "healthy"
    except Exception:
        return "unhealthy"

async def check_celery():
    """检查Celery状态"""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            return "healthy"
        return "unhealthy"
    except Exception:
        return "unhealthy"
```

### 3. 性能监控
```python
# app/middleware.py
import time
import structlog
from fastapi import Request, Response

logger = structlog.get_logger()

async def performance_middleware(request: Request, call_next):
    """性能监控中间件"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    logger.info(
        "request_processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 🔒 安全配置

### 1. 环境变量
```bash
# .env.prod
# 应用配置
APP_NAME=AI研发辅助平台
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ENVIRONMENT=production

# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:your-strong-password@postgres:5432/ai_platform
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# 加密配置
ENCRYPTION_KEY=your-fernet-encryption-key-here

# Redis配置
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# AI服务配置（根据需要配置）
OPENAI_API_KEY=your-openai-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key

# 文件存储配置
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=52428800  # 50MB

# 日志配置
LOG_LEVEL=INFO
SENTRY_DSN=your-sentry-dsn-here
```

### 2. 防火墙配置
```bash
# 只开放必要端口
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

---

**文档版本**: v1.0  
**最后更新**: 2024年12月  
**负责人**: 运维团队
