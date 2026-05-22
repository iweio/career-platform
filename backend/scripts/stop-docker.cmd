@echo off

rem Career Service AI Platform — Stop Script

echo ====================================
echo Career Service AI Platform 停止脚本
echo ====================================

docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Docker 未运行，无需停止
    pause
    exit /b 0
)

echo 1. 停止服务...
docker-compose down

if %ERRORLEVEL% neq 0 (
    echo 错误: 服务停止失败
    pause
    exit /b 1
)

echo 2. 系统已成功停止！
pause
