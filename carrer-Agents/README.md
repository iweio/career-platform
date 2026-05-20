# 职业智能体系统

一个基于 Docker 和 Flask 的职业智能体系统，提供简历分析、人岗匹配、职业规划、学习计划生成等功能。

## 功能特性

- 📄 简历分析和信息提取
- 🔍 人岗匹配和深度分析
- 📈 职业规划和发展路径
- 📚 学习计划生成和管理
- ✅ 每日任务生成和跟踪
- ✨ 智能润色和优化
- 📄 文档导出功能

## 系统架构

- **前端**：静态 HTML + JavaScript
- **后端**：Flask API
- **数据库**：MySQL + Neo4j
- **部署**：Docker Compose

## 快速开始

### 前提条件

- Docker Desktop 已安装并运行
- Windows 10/11 操作系统

### 启动系统

1. **下载项目代码**到本地目录
2. **双击运行** `start-system.cmd` 脚本
3. **等待系统启动**（约 30 秒）
4. **访问系统**：
   - 前端：http://localhost
   - 后端 API：http://localhost:5000
   - Neo4j 浏览器：http://localhost:7474

### 停止系统

- **双击运行** `stop-system.cmd` 脚本

## 系统初始化

系统启动时会自动完成以下初始化工作：

1. **数据库初始化**：
   - 创建所有必要的数据库表
   - 插入初始数据（用户、岗位、晋升路径）

2. **Neo4j 初始化**：
   - 创建岗位画像数据
   - 建立职业发展关系

3. **服务启动**：
   - MySQL 数据库服务
   - Neo4j 图数据库服务
   - 后端 API 服务
   - 前端 Nginx 服务

## 核心功能使用

### 1. 简历分析

1. 在首页上传简历或输入个人信息
2. 系统会自动提取和分析个人信息
3. 补充缺失的信息（如果需要）
4. 完成信息收集后进行深度分析

### 2. 人岗匹配

1. 完成简历分析后，点击「人岗匹配」
2. 系统会基于个人信息和岗位数据进行匹配
3. 显示匹配结果和推荐岗位

### 3. 职业规划

1. 完成人岗匹配后，点击「职业规划」
2. 系统会生成详细的职业发展规划
3. 显示职业路径、能力要求和时间节点

### 4. 学习计划

1. 完成职业规划后，点击「学习计划」
2. 系统会生成长期和短期学习计划
3. 可以查看和管理每日任务
4. 可以润色和调整学习计划
5. 可以导出学习计划为文档

## 技术栈

- **后端**：Python 3.11, Flask, SQLAlchemy, Py2neo
- **数据库**：MySQL 8.0, Neo4j 5
- **前端**：HTML, JavaScript, Bootstrap
- **容器化**：Docker, Docker Compose

## 项目结构

```
├── agents/             # 智能体模块
│   ├── career_planner/ # 职业规划智能体
│   ├── job_matcher/    # 人岗匹配智能体
│   ├── learning_plan/  # 学习计划智能体
│   ├── manager/        # 智能体管理器
│   └── resume_extractor/ # 简历提取智能体
├── static/             # 静态文件
├── templates/          # HTML 模板
├── uploads/            # 上传文件
├── api.py              # 主 API 文件
├── create_tables.sql   # 数据库表创建脚本
├── Dockerfile          # Docker 构建文件
├── docker-compose.yml  # Docker Compose 配置
├── init_database.sql   # 数据库初始化脚本
├── requirements.txt    # Python 依赖
├── start-system.cmd    # 启动脚本
└── stop-system.cmd     # 停止脚本
```

## 常见问题

### 1. 系统启动失败

- **检查 Docker**：确保 Docker Desktop 已运行
- **检查端口**：确保 80、3306、5000、7474、7687 端口未被占用
- **查看日志**：运行 `docker-compose logs` 查看详细错误信息

### 2. 数据库连接失败

- **等待初始化**：系统启动需要时间初始化数据库
- **检查配置**：确保 docker-compose.yml 中的数据库配置正确

### 3. 功能无法使用

- **检查服务状态**：运行 `docker-compose ps` 查看所有服务是否正常运行
- **查看 API 日志**：运行 `docker logs career-backend` 查看 API 错误信息

## 故障排除

### 重置系统

如果系统出现严重问题，可以执行以下步骤重置：

1. 运行 `stop-system.cmd` 停止所有服务
2. 删除数据卷：
   ```bash
   docker volume rm carrer-agents_mysql_data carrer-agents_neo4j_data
   ```
3. 重新运行 `start-system.cmd` 启动系统

### 查看日志

- **查看所有服务日志**：
  ```bash
  docker-compose logs
  ```

- **查看特定服务日志**：
  ```bash
  docker logs career-backend  # 查看后端 API 日志
  docker logs backend-mysql   # 查看 MySQL 日志
  docker logs backend-neo4j   # 查看 Neo4j 日志
  ```

## 部署说明

### 生产环境部署

1. **修改配置**：
   - 更新 docker-compose.yml 中的密码和环境变量
   - 设置 FLASK_ENV=production

2. **构建镜像**：
   ```bash
   docker-compose build
   ```

3. **启动服务**：
   ```bash
   docker-compose up -d
   ```

### 数据备份

- **备份 MySQL 数据**：
  ```bash
  docker exec -it backend-mysql mysqldump -u root -p job_db > backup.sql
  ```

- **备份 Neo4j 数据**：
  ```bash
  docker cp backend-neo4j:/data /path/to/backup
  ```

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系项目维护者。