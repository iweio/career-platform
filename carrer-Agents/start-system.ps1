<#
职业智能体系统启动脚本
此脚本使用 PowerShell 命令启动整个系统
#>

Write-Host "===================================="
Write-Host "职业智能体系统启动脚本"
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

Write-Host "1. 构建和启动服务..."
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 服务启动失败"
    Read-Host "按 Enter 键退出..."
    exit 1
}

Write-Host "2. 等待服务启动完成..."
Start-Sleep -Seconds 15

Write-Host "3. 检查服务状态..."
docker-compose ps

Write-Host "4. 系统启动完成！"
Write-Host ""
Write-Host "访问地址："
Write-Host "- 前端：http://localhost"
Write-Host "- 后端 API：http://localhost:5000"
Write-Host "- Neo4j 浏览器：http://localhost:7474"

Write-Host ""
Write-Host "系统已成功启动！"
Write-Host "您可以通过前端页面访问所有功能。"
Write-Host ""
Read-Host "按 Enter 键退出..."