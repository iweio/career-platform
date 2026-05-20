@echo off

rem 停止脚本 - 停止整个职业智能体系统

echo ====================================
echo 职业智能体系统停止脚本
echo ====================================

rem 检查 Docker 是否运行
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: Docker 未运行或未安装
    echo 请确保 Docker 已安装并启动
    pause
    exit /b 1
)

echo 1. 停止服务...
docker-compose down

if %ERRORLEVEL% neq 0 (
    echo 错误: 服务停止失败
    pause
    exit /b 1
)

echo 2. 检查服务状态...
docker-compose ps

echo 3. 系统已成功停止！
echo.  
echo 所有服务已停止。
echo 按任意键退出...
pause >nul