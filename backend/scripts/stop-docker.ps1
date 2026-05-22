Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Career Service AI Platform 停止脚本" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

try {
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker 未运行，无需停止" -ForegroundColor Yellow
        Read-Host "按任意键退出"
        exit 0
    }
} catch {
    Write-Host "Docker 未运行，无需停止" -ForegroundColor Yellow
    Read-Host "按任意键退出"
    exit 0
}

Write-Host ""
Write-Host "1. 停止服务..." -ForegroundColor Yellow
docker-compose down

if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 服务停止失败" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

Write-Host ""
Write-Host "2. 系统已成功停止！" -ForegroundColor Green

Read-Host "按任意键退出"
