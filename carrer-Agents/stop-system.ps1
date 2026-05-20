<#
职业智能体系统停止脚本
此脚本使用 PowerShell 命令停止整个系统
#>

Write-Host "===================================="
Write-Host "职业智能体系统停止脚本"
Write-Host "===================================="

# 检查 Docker 是否运行
try {
    docker info | Out-Null
    Write-Host "Docker 运行正常"
} catch {
    Write-Host "错误: Docker 未运行或未安装"
    Write-Host "请确保 Docker 已安装并启动"
    Read-Host "按 Enter 键退出..."
    exit 1
}

Write-Host "1. 停止服务..."
docker-compose down

if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 服务停止失败"
    Read-Host "按 Enter 键退出..."
    exit 1
}

Write-Host "2. 检查服务状态..."
docker-compose ps

Write-Host "3. 系统已成功停止！"
Write-Host ""
Write-Host "所有服务已停止。"
Write-Host ""
Read-Host "按 Enter 键退出..."