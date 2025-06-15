#!/bin/bash
# AI研发辅助平台 - 本地开发启动脚本

echo "🚀 启动 AI研发辅助平台本地开发环境"
echo "=================================="

# 检查是否安装了必要的依赖
echo "📋 检查环境依赖..."

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 18+"
    exit 1
fi

# 检查 Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 设置 Python 命令
PYTHON_CMD="python3"
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "✅ 环境检查通过"

# 检查后端环境配置
if [ ! -f "backend/.env" ]; then
    echo "⚠️  后端 .env 文件不存在，请复制 backend/env.example 为 backend/.env 并配置"
    echo "   生成示例密钥："
    echo "   SECRET_KEY: $($PYTHON_CMD -c 'import secrets; print(secrets.token_urlsafe(32))')"
    echo "   ENCRYPTION_KEY: $($PYTHON_CMD -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
    echo ""
fi

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

# 启动前端开发服务器（后台运行）
echo "🌐 启动前端开发服务器 (http://localhost:3000)..."
npm run dev &
FRONTEND_PID=$!

# 回到根目录
cd ..

# 安装后端依赖
echo "📦 安装后端依赖..."
cd backend
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    $PYTHON_CMD -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt 2>/dev/null || echo "requirements.txt 不存在，请手动安装依赖"

# 启动后端开发服务器
echo "🔧 启动后端开发服务器 (http://localhost:8000)..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 等待服务启动
sleep 3

echo ""
echo "🎉 开发环境启动完成！"
echo "=================================="
echo "前端地址: http://localhost:3000"
echo "后端地址: http://localhost:8000"
echo "API文档: http://localhost:8000/api/v1/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "echo '正在停止服务...'; kill $FRONTEND_PID $BACKEND_PID 2>/dev/null; exit 0" INT
wait 