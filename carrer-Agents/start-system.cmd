@echo off

rem 启动脚本 - 一键启动整个职业智能体系统

echo ====================================
echo 职业智能体系统启动脚本
echo ====================================

rem 检查 Docker 是否运行
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: Docker 未运行或未安装
    echo 请确保 Docker 已安装并启动
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

echo 4. 系统启动完成！
echo.  
echo 访问地址：
echo - 前端：http://localhost
echo - 后端 API：http://localhost:5000
echo - Neo4j 浏览器：http://localhost:7474

echo.  
echo 系统已成功启动！
echo 您可以通过前端页面访问所有功能。
echo.  
echo 按任意键退出...
pause >nul