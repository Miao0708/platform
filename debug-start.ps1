# AI研发辅助平台 - 调试模式启动脚本
# 此脚本将启动前后端并开启详细的接口链路调试

Write-Host "🔧 启动AI研发辅助平台 - 调试模式" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Yellow

# 设置调试环境变量
$env:DEBUG = "true"
$env:LOG_LEVEL = "DEBUG"

# 后端启动
Write-Host "🚀 启动后端服务（调试模式）..." -ForegroundColor Cyan
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", @"
Set-Location './backend'
Write-Host '📋 后端日志将显示以下详细信息:' -ForegroundColor Yellow
Write-Host '  📥 HTTP请求详情 (headers, body, params)' -ForegroundColor Gray
Write-Host '  📤 HTTP响应详情 (status, headers, data)' -ForegroundColor Gray
Write-Host '  🗄️ 数据库查询 (SQL, 执行时间)' -ForegroundColor Gray
Write-Host '  💥 错误信息 (异常堆栈跟踪)' -ForegroundColor Gray
Write-Host '  ⚡ 性能指标 (响应时间)' -ForegroundColor Gray
Write-Host ''
Write-Host '🎯 后端服务启动中...' -ForegroundColor Green
uvicorn app.main:app --reload --port=8000 --log-level debug
"@

# 等待后端启动
Start-Sleep -Seconds 5

# 前端启动
Write-Host "🎨 启动前端服务（调试模式）..." -ForegroundColor Cyan
Start-Process PowerShell -ArgumentList "-NoExit", "-Command", @"
Set-Location './frontend'
Write-Host '📋 前端日志将显示以下详细信息:' -ForegroundColor Yellow
Write-Host '  📤 API请求详情 (method, url, headers, body)' -ForegroundColor Gray
Write-Host '  📥 API响应详情 (status, data, 耗时)' -ForegroundColor Gray
Write-Host '  ❌ 请求错误详情 (错误信息, 状态码)' -ForegroundColor Gray
Write-Host '  🔗 请求链路追踪 (requestId)' -ForegroundColor Gray
Write-Host ''
Write-Host '💡 打开浏览器开发者工具查看详细日志' -ForegroundColor Blue
Write-Host '🎯 前端服务启动中...' -ForegroundColor Green
npm run dev
"@

Write-Host ""
Write-Host "📖 调试指南:" -ForegroundColor Yellow
Write-Host "  1. 后端日志在终端中实时显示" -ForegroundColor White
Write-Host "  2. 前端日志在浏览器控制台中查看" -ForegroundColor White
Write-Host "  3. 每个请求都有唯一的requestId用于链路追踪" -ForegroundColor White
Write-Host "  4. 可以通过日志过滤特定的API调用" -ForegroundColor White
Write-Host ""
Write-Host "🌐 访问地址:" -ForegroundColor Yellow
Write-Host "  前端: http://localhost:3000" -ForegroundColor Blue
Write-Host "  后端API: http://localhost:8000" -ForegroundColor Blue
Write-Host "  API文档: http://localhost:8000/api/v1/docs" -ForegroundColor Blue
Write-Host ""
Write-Host "按任意键继续..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 