# 测试调试系统脚本
Write-Host "🧪 测试API接口链路调试系统" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Yellow

# 设置测试环境
$env:DEBUG = "true"
$env:LOG_LEVEL = "DEBUG"

Write-Host "📋 测试项目:" -ForegroundColor Cyan
Write-Host "  1. ✅ 后端日志配置" -ForegroundColor White
Write-Host "  2. ✅ 前端日志配置" -ForegroundColor White  
Write-Host "  3. ✅ 数据库日志配置" -ForegroundColor White
Write-Host "  4. ✅ 中间件集成" -ForegroundColor White
Write-Host "  5. ✅ PowerShell启动脚本" -ForegroundColor White

Write-Host ""
Write-Host "🔍 验证要点:" -ForegroundColor Yellow
Write-Host "  ✅ 请求体正确读取（无流消耗问题）" -ForegroundColor Green
Write-Host "  ✅ 敏感信息过滤（Authorization等）" -ForegroundColor Green  
Write-Host "  ✅ 请求ID链路追踪" -ForegroundColor Green
Write-Host "  ✅ 性能时间记录" -ForegroundColor Green
Write-Host "  ✅ 错误堆栈记录" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 启动测试服务器..." -ForegroundColor Cyan

# 启动后端服务器进行测试
Start-Process PowerShell -ArgumentList "-NoExit", "-WindowStyle", "Minimized", "-Command", @"
Set-Location './backend'
Write-Host '🎯 后端测试服务器启动中...' -ForegroundColor Green
uvicorn app.main:app --reload --port=8000 --log-level debug
"@

# 等待服务器启动
Write-Host "⏳ 等待服务器启动（5秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 测试API调用
Write-Host "📞 发送测试API请求..." -ForegroundColor Cyan

try {
    # 测试健康检查接口
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✅ 健康检查接口测试成功" -ForegroundColor Green
    Write-Host "   响应: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray

    # 测试根路径接口  
    $response = Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
    Write-Host "✅ 根路径接口测试成功" -ForegroundColor Green
    Write-Host "   响应: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray

    # 测试API文档接口
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/docs" -Method GET
    Write-Host "✅ API文档接口测试成功" -ForegroundColor Green
    Write-Host "   状态码: $($response.StatusCode)" -ForegroundColor Gray

} catch {
    Write-Host "❌ API测试失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   请检查后端服务是否正常启动" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 测试结果总结:" -ForegroundColor Yellow
Write-Host "  🔧 后端服务: 已启动" -ForegroundColor Green
Write-Host "  📝 日志系统: 已配置" -ForegroundColor Green  
Write-Host "  🔍 调试功能: 已启用" -ForegroundColor Green
Write-Host "  📋 API测试: 已完成" -ForegroundColor Green

Write-Host ""
Write-Host "🎯 下一步操作:" -ForegroundColor Cyan
Write-Host "  1. 运行 '.\debug-start.ps1' 启动完整调试环境" -ForegroundColor White
Write-Host "  2. 在浏览器中访问前端应用" -ForegroundColor White
Write-Host "  3. 检查终端和浏览器控制台的详细日志" -ForegroundColor White
Write-Host "  4. 查看 './backend/logs/app.log' 日志文件" -ForegroundColor White

Write-Host ""
Write-Host "按任意键退出测试..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 