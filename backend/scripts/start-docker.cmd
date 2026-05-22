@echo off

rem Career Service AI Platform — Start Script

echo ====================================
echo Career Service AI Platform 启动脚本
echo ====================================

docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: Docker 未运行或未安装
    pause
    exit /b 1
)

echo 1. 构建和启动服务...
docker-compose up -d --build

if %ERRORLEVEL% neq 0 (
    echo 错误: 服务启动失败
    pause
    exit /b 1
)

echo 2. 等待服务启动完成...
timeout /t 15 /nobreak >nul

echo 3. 检查服务状态...
docker-compose ps

echo.
echo 访问地址：
echo - 前端：http://localhost
echo - 后端 API：http://localhost:8000
echo - API 文档：http://localhost:8000/docs
echo - Neo4j 浏览器：http://localhost:7474
echo.
echo 系统已成功启动！
pause
