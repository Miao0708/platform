# AI研发辅助平台 - 部署指南

## 📋 部署概述

### 系统要求
- **Node.js**: 18.0+ 
- **npm/yarn/pnpm**: 最新版本
- **内存**: 最小2GB，推荐4GB+
- **存储**: 最小10GB可用空间
- **网络**: 稳定的互联网连接（用于AI模型API调用）

### 支持的部署环境
- **开发环境**: 本地开发服务器
- **测试环境**: Docker容器部署
- **生产环境**: Nginx + Docker + CDN

## 🛠️ 开发环境部署

### 1. 环境准备
```bash
# 检查Node.js版本
node --version  # 应该 >= 18.0

# 检查npm版本
npm --version

# 安装pnpm (推荐)
npm install -g pnpm
```

### 2. 项目克隆和依赖安装
```bash
# 克隆项目
git clone https://github.com/your-org/ai-dev-platform.git
cd ai-dev-platform

# 安装依赖
pnpm install

# 或使用npm
npm install
```

### 3. 环境配置
```bash
# 复制环境变量文件
cp .env.example .env.development

# 编辑环境变量
vim .env.development
```

**.env.development 配置示例**
```bash
# API配置
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_TITLE=AI研发辅助平台
VITE_APP_ENV=development

# 功能开关
VITE_ENABLE_MOCK=true
VITE_ENABLE_DEBUG=true

# 第三方服务
VITE_UPLOAD_URL=http://localhost:8000/upload
```

### 4. 启动开发服务器
```bash
# 启动开发服务器
pnpm dev

# 或使用npm
npm run dev
```

访问 http://localhost:3000 查看应用

### 5. 开发工具配置

#### VS Code 推荐插件
```json
{
  "recommendations": [
    "vue.volar",
    "vue.typescript-vue-plugin",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint"
  ]
}
```

#### ESLint 配置
```javascript
// .eslintrc.js
module.exports = {
  extends: [
    '@vue/typescript/recommended',
    'plugin:vue/vue3-recommended'
  ],
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-explicit-any': 'warn'
  }
}
```

## 🐳 Docker 部署

### 1. Dockerfile
```dockerfile
# 多阶段构建
FROM node:18-alpine as builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./
COPY pnpm-lock.yaml ./

# 安装pnpm
RUN npm install -g pnpm

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建应用
RUN pnpm build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 2. Nginx 配置
```nginx
# nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # 基础配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
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
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # SPA路由支持
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # API代理
        location /api/ {
            proxy_pass http://backend:8000/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # 安全头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    }
}
```

### 3. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    depends_on:
      - backend
    networks:
      - app-network
    restart: unless-stopped

  backend:
    image: ai-platform-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/aiplatform
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    networks:
      - app-network
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=aiplatform
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### 4. 构建和运行
```bash
# 构建镜像
docker build -t ai-platform-frontend .

# 使用docker-compose启动
docker-compose up -d

# 查看日志
docker-compose logs -f frontend

# 停止服务
docker-compose down
```

## 🚀 生产环境部署

### 1. 构建优化
```bash
# 生产构建
pnpm build

# 分析构建产物
pnpm build --report
```

### 2. 环境变量配置
**.env.production**
```bash
# API配置
VITE_API_BASE_URL=https://api.yourdomain.com/api
VITE_APP_TITLE=AI研发辅助平台
VITE_APP_ENV=production

# 功能开关
VITE_ENABLE_MOCK=false
VITE_ENABLE_DEBUG=false

# CDN配置
VITE_CDN_URL=https://cdn.yourdomain.com

# 监控配置
VITE_SENTRY_DSN=https://your-sentry-dsn
```

### 3. CDN 配置
```javascript
// vite.config.ts
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      external: ['vue', 'vue-router', 'pinia'],
      output: {
        globals: {
          vue: 'Vue',
          'vue-router': 'VueRouter',
          pinia: 'Pinia'
        }
      }
    }
  }
})
```

### 4. 性能优化配置
```nginx
# nginx生产配置
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    
    # 静态资源优化
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # 启用Brotli压缩
        brotli on;
        brotli_comp_level 6;
        brotli_types text/plain text/css application/javascript;
    }
    
    # 预加载关键资源
    location = /index.html {
        add_header Link "</assets/app.js>; rel=preload; as=script";
        add_header Link "</assets/app.css>; rel=preload; as=style";
    }
}
```

## 🔧 CI/CD 配置

### 1. GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'pnpm'
        
    - name: Install pnpm
      run: npm install -g pnpm
      
    - name: Install dependencies
      run: pnpm install --frozen-lockfile
      
    - name: Run tests
      run: pnpm test
      
    - name: Build application
      run: pnpm build
      env:
        VITE_API_BASE_URL: ${{ secrets.API_BASE_URL }}
        
    - name: Build Docker image
      run: |
        docker build -t ai-platform-frontend:${{ github.sha }} .
        docker tag ai-platform-frontend:${{ github.sha }} ai-platform-frontend:latest
        
    - name: Deploy to production
      run: |
        # 部署脚本
        ./scripts/deploy.sh
```

### 2. 部署脚本
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 开始部署..."

# 备份当前版本
docker tag ai-platform-frontend:latest ai-platform-frontend:backup

# 停止当前服务
docker-compose down

# 拉取最新镜像
docker pull ai-platform-frontend:latest

# 启动新服务
docker-compose up -d

# 健康检查
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
if curl -f http://localhost/health; then
    echo "✅ 部署成功!"
    # 清理备份镜像
    docker rmi ai-platform-frontend:backup
else
    echo "❌ 部署失败，回滚到上一版本"
    docker tag ai-platform-frontend:backup ai-platform-frontend:latest
    docker-compose up -d
    exit 1
fi
```

## 📊 监控和日志

### 1. 应用监控
```typescript
// src/utils/monitoring.ts
import * as Sentry from '@sentry/vue'

// 错误监控
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.VITE_APP_ENV,
  tracesSampleRate: 0.1
})

// 性能监控
export const trackPerformance = (name: string, duration: number) => {
  if (import.meta.env.PROD) {
    // 发送性能数据到监控服务
    fetch('/api/metrics', {
      method: 'POST',
      body: JSON.stringify({ name, duration, timestamp: Date.now() })
    })
  }
}
```

### 2. 日志配置
```nginx
# nginx日志配置
http {
    # 自定义日志格式
    log_format json_combined escape=json
        '{'
        '"time_local":"$time_local",'
        '"remote_addr":"$remote_addr",'
        '"request":"$request",'
        '"status":"$status",'
        '"body_bytes_sent":"$body_bytes_sent",'
        '"request_time":"$request_time",'
        '"http_user_agent":"$http_user_agent"'
        '}';
    
    access_log /var/log/nginx/access.log json_combined;
}
```

## 🔒 安全配置

### 1. HTTPS 配置
```bash
# 使用Let's Encrypt获取SSL证书
certbot --nginx -d yourdomain.com

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### 2. 安全头配置
```nginx
# 安全头
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
```

## 🚨 故障排除

### 常见问题

#### 1. 构建失败
```bash
# 清理缓存
pnpm store prune
rm -rf node_modules
pnpm install

# 检查Node.js版本
node --version
```

#### 2. 内存不足
```bash
# 增加Node.js内存限制
export NODE_OPTIONS="--max-old-space-size=4096"
pnpm build
```

#### 3. 网络问题
```bash
# 使用国内镜像
pnpm config set registry https://registry.npmmirror.com/
```

#### 4. Docker构建慢
```dockerfile
# 使用多阶段构建和缓存
FROM node:18-alpine as deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
```

### 日志查看
```bash
# 查看应用日志
docker-compose logs -f frontend

# 查看nginx日志
docker exec -it container_name tail -f /var/log/nginx/access.log

# 查看系统资源
docker stats
```

## 📋 部署检查清单

### 部署前检查
- [ ] 代码已合并到主分支
- [ ] 所有测试通过
- [ ] 环境变量已配置
- [ ] SSL证书有效
- [ ] 备份已创建

### 部署后检查
- [ ] 应用可正常访问
- [ ] 所有功能正常
- [ ] 性能指标正常
- [ ] 错误日志无异常
- [ ] 监控告警正常

---

**文档版本**：v2.0  
**最后更新**：2024年12月  
**负责人**：运维团队
