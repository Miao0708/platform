# AI研发辅助平台 - Windows本地开发启动脚本

Write-Host "🚀 启动 AI研发辅助平台本地开发环境" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# 检查是否安装了必要的依赖
Write-Host "📋 检查环境依赖..." -ForegroundColor Yellow

# 检查 Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js 未安装，请先安装 Node.js 18+" -ForegroundColor Red
    exit 1
}

# 检查 Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    $pythonCmd = "python"
} catch {
    try {
        $pythonVersion = python3 --version
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        $pythonCmd = "python3"
    } catch {
        Write-Host "❌ Python 未安装，请先安装 Python 3.8+" -ForegroundColor Red
        exit 1
    }
}

# 检查后端环境配置
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  后端 .env 文件不存在，请复制 backend\env.example 为 backend\.env 并配置" -ForegroundColor Yellow
    Write-Host "   生成示例密钥：" -ForegroundColor Cyan
    $secretKey = & $pythonCmd -c "import secrets; print(secrets.token_urlsafe(32))"
    $encryptionKey = & $pythonCmd -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    Write-Host "   SECRET_KEY: $secretKey" -ForegroundColor Cyan
    Write-Host "   ENCRYPTION_KEY: $encryptionKey" -ForegroundColor Cyan
    Write-Host ""
}

# 启动前端开发服务器
Write-Host "📦 启动前端开发服务器..." -ForegroundColor Yellow
Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "安装前端依赖..." -ForegroundColor Cyan
    npm install
}

# 启动前端（新窗口）
Write-Host "🌐 启动前端开发服务器 (http://localhost:3000)..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock { 
    Set-Location $using:PWD\frontend
    npm run dev 
}

# 回到根目录
Set-Location ..

# 启动后端开发服务器
Write-Host "📦 启动后端开发服务器..." -ForegroundColor Yellow
Set-Location backend

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "创建Python虚拟环境..." -ForegroundColor Cyan
    & $pythonCmd -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# 安装依赖
if (Test-Path "requirements.txt") {
    Write-Host "安装后端依赖..." -ForegroundColor Cyan
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt 不存在，请手动安装依赖" -ForegroundColor Yellow
}

# 启动后端
Write-Host "🔧 启动后端开发服务器 (http://localhost:8000)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock { 
    Set-Location $using:PWD\backend
    & ".\venv\Scripts\Activate.ps1"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 
}

# 等待服务启动
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "🎉 开发环境启动完成！" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host "前端地址: http://localhost:3000" -ForegroundColor Cyan
Write-Host "后端地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API文档: http://localhost:8000/api/v1/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow

# 等待用户中断
try {
    while ($true) {
        Start-Sleep -Seconds 1
        # 检查任务状态
        if ($frontendJob.State -eq "Failed" -or $backendJob.State -eq "Failed") {
            Write-Host "服务启动失败，请检查日志" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host "正在停止服务..." -ForegroundColor Yellow
    Stop-Job $frontendJob -Force
    Stop-Job $backendJob -Force
    Remove-Job $frontendJob -Force
    Remove-Job $backendJob -Force
} 