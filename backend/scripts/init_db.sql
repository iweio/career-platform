-- Career Service AI Platform - Consolidated Database Schema
-- Mounted as /docker-entrypoint-initdb.d/init_db.sql

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    city VARCHAR(100),
    salary_range VARCHAR(100),
    job_description TEXT,
    requirements TEXT,
    publish_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_jobs_title (job_title),
    INDEX idx_jobs_industry (industry)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    profile_data JSON NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    match_score DECIMAL(5,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_favorite_user_job (user_id, job_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS career_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    target_position VARCHAR(255),
    target_company VARCHAR(255),
    timeline_months INT,
    status VARCHAR(50) DEFAULT 'active',
    plan_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS job_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    profile_data JSON,
    summary VARCHAR(1024),
    core_skills JSON,
    career_path JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS promotion_transition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT,
    current_role VARCHAR(255) NOT NULL,
    next_role VARCHAR(255) NOT NULL,
    required_skills JSON,
    years_exp INT,
    transition_type VARCHAR(50) DEFAULT 'promotion',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS matching_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_name VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    city VARCHAR(100),
    match_score DECIMAL(5,2),
    report_data JSON,
    publish_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS learning_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    target_job VARCHAR(255),
    plan_type VARCHAR(50) DEFAULT '长期',
    phases JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS daily_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    phase_index INT DEFAULT 0,
    task_date DATE,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1024),
    duration VARCHAR(50),
    resources JSON,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed data: test user (password = "password123", bcrypt hash)
INSERT INTO users (username, email, password_hash) VALUES
('testuser', 'test@example.com', '$2b$12$LJ3m4ys3uz0Gv0gMOsYmNe8JI8k/.dRgRv0cOx5vGJy0fkKzJKHpy');

-- Seed data: sample jobs
INSERT INTO jobs (job_title, company, industry, city, salary_range, job_description, requirements, publish_date) VALUES
('Python后端开发工程师', '字节跳动', '互联网/IT', '北京', '25k-50k', '负责后端服务的设计与开发，构建高可用、高并发的分布式系统。', '熟悉Python、Django/FastAPI、MySQL、Redis、分布式系统。3年以上后端开发经验。', CURDATE()),
('前端开发工程师', '阿里巴巴', '互联网/IT', '杭州', '20k-45k', '负责Web前端开发，与设计师和后端紧密协作，实现优秀的用户体验。', '熟悉Vue.js/React、TypeScript、CSS3、前端工程化。', CURDATE()),
('数据分析师', '腾讯', '互联网/IT', '深圳', '18k-35k', '负责数据收集、清洗、分析与可视化，为业务决策提供数据支持。', '熟悉Python/SQL、统计分析、机器学习基础、数据可视化工具。', CURDATE()),
('产品经理', '美团', '互联网/IT', '上海', '22k-40k', '负责产品规划、需求分析与项目管理，推动产品从概念到上线。', '熟悉产品设计方法论、数据分析、项目管理、优秀的沟通能力。', CURDATE());

-- Seed data: promotion paths
INSERT INTO promotion_transition (job_id, current_role, next_role, required_skills, years_exp, transition_type) VALUES
(1, '初级Python开发', '中级Python开发', '["Python","Django","MySQL","Redis"]', 2, 'promotion'),
(1, '中级Python开发', '高级Python开发', '["系统设计","分布式","Docker","微服务"]', 3, 'promotion'),
(2, '初级前端开发', '中级前端开发', '["Vue.js","React","TypeScript","Webpack"]', 2, 'promotion'),
(2, '中级前端开发', '高级前端开发', '["架构设计","性能优化","工程化","Node.js"]', 3, 'promotion'),
(3, '初级数据分析师', '高级数据分析师', '["Python","机器学习","SQL","数据可视化"]', 3, 'promotion'),
(4, '产品助理', '产品经理', '["需求分析","竞品分析","原型设计","项目管理"]', 2, 'promotion');

-- ============================================================
-- Phase 2: 前端静态数据入库
-- ============================================================

-- 职业分类卡片（Home.vue 左侧面板）
CREATE TABLE IF NOT EXISTS job_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '分类名',
    icon VARCHAR(50) COMMENT 'Element Plus icon 名',
    tag VARCHAR(30) COMMENT '标签',
    sort_order INT DEFAULT 0,
    insight_scarcity VARCHAR(30) COMMENT '稀缺度',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO job_categories (name, icon, tag, sort_order, insight_scarcity) VALUES
('后端开发', 'Monitor', '高需求', 1, '高需求'),
('前端开发', 'Grid', '热门', 2, '热门'),
('AI / 机器学习', 'Cpu', '新兴', 3, '稀缺'),
('数据分析', 'DataAnalysis', '高薪', 4, '热门'),
('产品经理', 'User', '管理岗', 5, '稳定'),
('UI / UX 设计', 'Brush', '创意', 6, '稳定'),
('网络安全', 'Lock', '稀缺', 7, '稀缺'),
('云计算', 'Cloudy', '增长快', 8, '高需求'),
('移动端开发', 'Iphone', '稳定', 9, '稳定'),
('测试开发', 'Checked', '基础岗', 10, '稳定');

-- 学习计划模板
CREATE TABLE IF NOT EXISTS plan_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) COMMENT '模板名',
    target_job VARCHAR(100),
    plan_type VARCHAR(50) DEFAULT '长期',
    phases JSON COMMENT '阶段数组',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO plan_templates (name, target_job, plan_type, phases) VALUES
('Java 高级架构师之路', 'Java后端开发', '长期', '[
  {"phase": 1, "title": "Java 核心深化与架构基础", "duration": "2-3个月", "goals": "深化 JVM 与并发编程，掌握微服务分布式核心体系", "items": ["JUC 并发工具包", "JVM 垃圾回收调优", "Spring Cloud Alibaba (Nacos/Sentinel)", "消息中间件原理 (Kafka)"]},
  {"phase": 2, "title": "性能调优与云原生技术栈", "duration": "2-3个月", "goals": "掌握大规模系统调优，熟练运用 K8s 进行容器化运维", "items": ["MySQL 索引与 SQL 调优", "Redis 集群方案", "Kubernetes 编排", "Prometheus 可观测性监控"]},
  {"phase": 3, "title": "领域驱动设计 (DDD) 与架构演进", "duration": "1-2个月", "goals": "掌握复杂业务建模方法，建立整洁架构思维", "items": ["限界上下文划分", "聚合根设计", "六边形架构", "代码重构与设计模式深度应用"]},
  {"phase": 4, "title": "综合实战与软技能提升", "duration": "持续进行", "goals": "提升技术方案评审、团队协作及全栈项目主导能力", "items": ["编写高质量技术设计方案", "敏捷开发管理", "跨团队沟通", "技术影响力建设 (博客/开源)"]}
]');

-- 补充更多岗位种子数据（从前端 post-sphere 节点 + 常见岗位）
INSERT INTO jobs (job_title, company, industry, city, salary_range, job_description, requirements, publish_date) VALUES
('AI算法工程师', '百度', '互联网/IT', '北京', '35k-70k', '负责深度学习模型研发与优化，推动AI技术在核心业务中的落地。', '熟悉Python/PyTorch/TensorFlow、深度学习、NLP/CV。硕士及以上学历。', CURDATE()),
('网络安全工程师', '奇安信', '信息安全', '北京', '20k-40k', '负责企业安全防护体系建设，渗透测试与漏洞挖掘。', '熟悉网络协议、渗透测试、安全工具（Burp Suite/Metasploit）、CISP/OSCP认证优先。', CURDATE()),
('UI/UX设计师', '网易', '互联网/IT', '广州', '18k-35k', '负责产品界面设计与用户体验优化，产出高保真原型。', '精通Figma/Sketch、熟悉设计系统、有B端/C端设计经验。', CURDATE()),
('云计算架构师', '华为', '云计算', '深圳', '40k-80k', '负责云平台架构设计与技术规划，推动云原生转型。', '熟悉Kubernetes/Docker、OpenStack、分布式存储、5年以上云计算经验。', CURDATE()),
('移动端开发工程师', '小米', '互联网/IT', '北京', '22k-45k', '负责iOS/Android客户端开发，优化应用性能与用户体验。', '熟悉Swift/Kotlin、Flutter/React Native、移动端性能优化。', CURDATE()),
('测试开发工程师', '京东', '互联网/IT', '北京', '20k-40k', '负责自动化测试框架搭建，质量保障体系建设。', '熟悉Python/Java、Selenium/Appium、CI/CD、性能测试。', CURDATE()),
('全栈开发工程师', '滴滴', '互联网/IT', '北京', '30k-55k', '负责全栈应用开发，从前端到后端完整交付。', '熟悉React/Vue + Node.js/Python、数据库设计、DevOps。', CURDATE()),
('运维SRE工程师', 'B站', '互联网/IT', '上海', '25k-50k', '负责线上服务稳定性保障，自动化运维平台建设。', '熟悉Linux、Kubernetes、Prometheus、Python/Go、故障处理。', CURDATE()),
('游戏开发工程师', '米哈游', '游戏', '上海', '30k-60k', '负责游戏客户端/服务端开发，引擎优化与工具链建设。', '熟悉Unity/Unreal、C++/C#、图形学、游戏服务器架构。', CURDATE()),
('物联网工程师', '大疆', '硬件/智能', '深圳', '25k-50k', '负责IoT平台开发，设备接入与数据管道建设。', '熟悉C/Python、MQTT/CoAP、嵌入式Linux、边缘计算。', CURDATE()),
('交互设计师', 'Soul', '社交', '上海', '18k-35k', '负责产品交互设计，用户研究与可用性测试。', '熟悉交互设计方法论、用户研究、原型设计、数据驱动设计。', CURDATE());

-- 为新增岗位补充晋升路径
INSERT INTO promotion_transition (job_id, current_role, next_role, required_skills, years_exp, transition_type) VALUES
(5, '初级AI算法工程师', '高级AI算法工程师', '["Python","深度学习","PyTorch","模型优化"]', 3, 'promotion'),
(6, '初级安全工程师', '高级安全工程师', '["渗透测试","安全架构","应急响应","CISP"]', 3, 'promotion'),
(7, '初级UI设计师', '高级UI设计师', '["Figma","设计系统","用户研究","动效设计"]', 2, 'promotion'),
(8, '云架构师', '首席云架构师', '["Kubernetes","OpenStack","多云管理","技术规划"]', 5, 'promotion'),
(9, '初级移动开发', '高级移动开发', '["Swift/Kotlin","性能优化","跨平台","架构设计"]', 3, 'promotion'),
(10, '初级测试开发', '高级测试开发', '["自动化框架","CI/CD","性能测试","质量体系"]', 2, 'promotion'),
(11, '全栈开发', '高级全栈开发', '["前后端架构","DevOps","数据库","系统设计"]', 3, 'promotion'),
(12, '初级SRE', '高级SRE', '["Kubernetes","Prometheus","故障处理","自动化运维"]', 3, 'promotion'),
(13, '初级游戏开发', '高级游戏开发', '["Unity/Unreal","图形学","游戏架构","性能优化"]', 3, 'promotion'),
(14, '初级IoT开发', '高级IoT开发', '["嵌入式","MQTT","边缘计算","传感器"]', 2, 'promotion'),
(15, '初级交互设计师', '高级交互设计师', '["用户研究","交互设计","原型设计","数据驱动"]', 2, 'promotion'),
(1, '高级Python开发', 'Python架构师', '["分布式架构","技术管理","团队领导","技术规划"]', 5, 'promotion'),
(2, '高级前端开发', '前端架构师', '["前端架构","技术选型","团队管理","工程化体系"]', 5, 'promotion');
