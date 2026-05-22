Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Career Service AI Platform 启动脚本" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

try {
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误: Docker 未运行或未安装" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
} catch {
    Write-Host "错误: Docker 未运行或未安装" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

Write-Host ""
Write-Host "1. 构建和启动服务..." -ForegroundColor Yellow
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 服务启动失败" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

Write-Host "2. 等待服务启动完成..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "3. 检查服务状态..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "系统已成功启动！" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "访问地址："
Write-Host "  - 前端：    http://localhost"
Write-Host "  - 后端 API： http://localhost:8000"
Write-Host "  - API 文档： http://localhost:8000/docs"
Write-Host "  - Neo4j：    http://localhost:7474"
Write-Host ""

Read-Host "按任意键退出"
