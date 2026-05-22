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
    user_id INT NOT NULL UNIQUE,
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

-- ============================================================
-- Phase 7: 大岗位族匹配 + Neo4j 建图
-- ============================================================

-- 注意：career_plans.user_id 需要 UNIQUE 约束（已在 CREATE TABLE 更新）
-- 如果是存量 DB，需手动：ALTER TABLE career_plans ADD UNIQUE INDEX uq_career_plans_user (user_id);

-- 7.1 jobs 表加 category_id
ALTER TABLE jobs ADD COLUMN category_id INT NULL;
ALTER TABLE jobs ADD FOREIGN KEY (category_id) REFERENCES job_categories(id);

-- 7.2 job_categories 加 4 列（description / core_skills / promotion_path / transition_to）
ALTER TABLE job_categories ADD COLUMN description TEXT COMMENT '岗位族描述，用于向量化';
ALTER TABLE job_categories ADD COLUMN core_skills JSON COMMENT '核心技能列表';
ALTER TABLE job_categories ADD COLUMN promotion_path JSON COMMENT '晋升路径，入Neo4j';
ALTER TABLE job_categories ADD COLUMN transition_to JSON COMMENT '可转岗方向';

-- 7.3 更新 15 个职位 → 10 大岗位族映射
UPDATE jobs SET category_id = 1  WHERE id IN (1, 11);
UPDATE jobs SET category_id = 2  WHERE id = 2;
UPDATE jobs SET category_id = 3  WHERE id = 5;
UPDATE jobs SET category_id = 4  WHERE id = 3;
UPDATE jobs SET category_id = 5  WHERE id = 4;
UPDATE jobs SET category_id = 6  WHERE id = 7;
UPDATE jobs SET category_id = 7  WHERE id = 6;
UPDATE jobs SET category_id = 8  WHERE id IN (8, 12);
UPDATE jobs SET category_id = 9  WHERE id IN (9, 13, 14);
UPDATE jobs SET category_id = 10 WHERE id = 10;

-- 7.4 10 大岗位族 placeholder 描述（用户后续提供真实数据）
UPDATE job_categories SET
  description = '后端开发工程师负责服务器端应用的设计、开发和维护。核心工作包括API接口设计、数据库建模、业务逻辑实现、系统性能优化和安全防护。需要掌握至少一门后端语言（如Java/Python/Go/Node.js），熟悉主流框架、关系型与非关系型数据库，了解分布式系统、消息队列、微服务架构等。',
  core_skills = '["编程语言(Java/Python/Go)", "数据库(MySQL/Redis)", "框架(Spring/Django)", "分布式系统", "消息队列", "API设计", "性能优化", "安全防护"]',
  promotion_path = '[{"stage":"初级后端开发","goal":"独立完成功能模块","salary":"8-15K","timeline":"0-2年"},{"stage":"中级后端开发","goal":"承担核心模块设计与优化","salary":"15-30K","timeline":"2-5年"},{"stage":"高级后端开发","goal":"系统架构设计","salary":"30-50K","timeline":"5-8年"},{"stage":"架构师/技术总监","goal":"技术规划与团队管理","salary":"50K+","timeline":"8年+"}]',
  transition_to = '[2, 3, 8]'
WHERE id = 1;

UPDATE job_categories SET
  description = '前端开发工程师负责Web和移动端用户界面的开发。工作内容包括页面布局、交互实现、状态管理、性能优化和跨浏览器兼容。需要精通HTML/CSS/JavaScript，掌握主流框架（React/Vue/Angular），了解前端工程化、构建工具、响应式设计和用户体验原则。',
  core_skills = '["HTML/CSS", "JavaScript/TypeScript", "React/Vue", "前端工程化", "性能优化", "响应式设计", "浏览器原理", "Node.js"]',
  promotion_path = '[{"stage":"初级前端开发","goal":"独立完成页面开发","salary":"8-15K","timeline":"0-2年"},{"stage":"中级前端开发","goal":"复杂交互与性能优化","salary":"15-30K","timeline":"2-5年"},{"stage":"高级前端开发","goal":"前端架构设计","salary":"30-50K","timeline":"5-8年"},{"stage":"前端架构师","goal":"技术选型与团队管理","salary":"50K+","timeline":"8年+"}]',
  transition_to = '[1, 6, 9]'
WHERE id = 2;

UPDATE job_categories SET
  description = 'AI/机器学习工程师负责算法模型的研发、训练和部署。工作内容包括数据预处理、特征工程、模型选型与调优、模型压缩与推理加速。需要扎实的数学基础（线性代数/概率论/优化理论），精通Python和深度学习框架，了解NLP/CV/推荐系统等方向。',
  core_skills = '["Python", "PyTorch/TensorFlow", "深度学习", "特征工程", "模型优化", "NLP/CV", "数据处理", "MCP服务"]',
  promotion_path = '[{"stage":"初级AI工程师","goal":"在指导下完成模型训练","salary":"15-25K","timeline":"0-2年"},{"stage":"中级AI工程师","goal":"独立完成模型选型与优化","salary":"25-45K","timeline":"2-5年"},{"stage":"高级AI工程师","goal":"算法创新与系统设计","salary":"45-70K","timeline":"5-8年"},{"stage":"AI科学家/技术总监","goal":"前沿研究方向制定","salary":"70K+","timeline":"8年+"}]',
  transition_to = '[1, 4]'
WHERE id = 3;

UPDATE job_categories SET
  description = '数据分析师负责从数据中提取业务洞察。工作内容包括数据采集与清洗、统计分析与建模、数据可视化与报告撰写。需要熟练使用SQL和Python/R，掌握统计学方法，了解常见的BI工具（Tableau/PowerBI/FineBI），具备良好的业务理解和沟通能力。',
  core_skills = '["SQL", "Python/R", "统计学", "数据可视化", "BI工具", "Excel", "业务分析", "机器学习基础"]',
  promotion_path = '[{"stage":"初级数据分析师","goal":"完成日常取数与报表","salary":"8-15K","timeline":"0-2年"},{"stage":"中级数据分析师","goal":"独立完成分析项目","salary":"15-25K","timeline":"2-4年"},{"stage":"高级数据分析师","goal":"业务策略建议","salary":"25-40K","timeline":"4-7年"},{"stage":"数据总监","goal":"数据驱动决策体系","salary":"40K+","timeline":"7年+"}]',
  transition_to = '[1, 3]'
WHERE id = 4;

UPDATE job_categories SET
  description = '产品经理负责产品从概念到上线的全生命周期管理。工作包括需求调研与分析、产品规划与路线图制定、PRD撰写、项目管理与跨团队协调。需要优秀的逻辑思维、沟通表达和数据分析能力，了解用户体验设计和商业分析方法。',
  core_skills = '["需求分析", "PRD撰写", "原型设计(Figma/Axure)", "数据分析", "项目管理", "用户研究", "商业分析", "沟通协调"]',
  promotion_path = '[{"stage":"产品助理","goal":"协助产品文档与需求整理","salary":"6-12K","timeline":"0-1年"},{"stage":"产品经理","goal":"独立负责产品模块","salary":"12-25K","timeline":"1-4年"},{"stage":"高级产品经理","goal":"产品线与团队管理","salary":"25-40K","timeline":"4-7年"},{"stage":"产品总监/VP","goal":"公司级产品战略","salary":"40K+","timeline":"7年+"}]',
  transition_to = '[4, 6]'
WHERE id = 5;

UPDATE job_categories SET
  description = 'UI/UX设计师负责产品界面视觉设计和用户体验优化。工作包括用户研究、信息架构、交互设计、视觉设计、设计规范制定和可用性测试。需要精通设计工具（Figma/Sketch），了解前端开发基础，具备审美能力和用户共情能力。',
  core_skills = '["Figma/Sketch", "交互设计", "视觉设计", "用户研究", "设计系统", "原型设计", "可用性测试", "前端基础"]',
  promotion_path = '[{"stage":"初级UI设计师","goal":"完成页面与Banner设计","salary":"6-12K","timeline":"0-2年"},{"stage":"中级UI/UX设计师","goal":"独立完成产品设计","salary":"12-22K","timeline":"2-5年"},{"stage":"高级体验设计师","goal":"设计系统与策略","salary":"22-35K","timeline":"5-8年"},{"stage":"设计总监","goal":"品牌与设计团队管理","salary":"35K+","timeline":"8年+"}]',
  transition_to = '[2, 5]'
WHERE id = 6;

UPDATE job_categories SET
  description = '网络安全工程师负责企业信息安全防护体系建设。工作包括漏洞扫描与渗透测试、安全事件响应、安全策略制定、等保合规审计。需要熟悉网络协议与操作系统原理，掌握常见安全工具和攻防技术，了解等级保护与数据安全法规。',
  core_skills = '["网络协议", "渗透测试", "漏洞挖掘", "安全工具(Burp/Metasploit)", "应急响应", "等保合规", "日志分析", "脚本(Python/Bash)"]',
  promotion_path = '[{"stage":"初级安全工程师","goal":"参与渗透测试与漏洞修复","salary":"10-18K","timeline":"0-2年"},{"stage":"中级安全工程师","goal":"独立完成安全评估","salary":"18-30K","timeline":"2-5年"},{"stage":"高级安全工程师","goal":"安全架构设计","salary":"30-50K","timeline":"5-8年"},{"stage":"安全总监/CISO","goal":"企业安全战略","salary":"50K+","timeline":"8年+"}]',
  transition_to = '[1, 8]'
WHERE id = 7;

UPDATE job_categories SET
  description = '云计算工程师负责云平台架构设计、运维和优化。工作包括云资源规划与调度、容器编排与管理、自动化运维、成本优化和云安全管理。需要熟悉主流云平台（AWS/阿里云/华为云）、Kubernetes生态、Terraform等IaC工具和Linux系统管理。',
  core_skills = '["AWS/阿里云", "Kubernetes", "Docker", "Terraform/IaC", "Linux", "自动化运维", "Prometheus", "云安全"]',
  promotion_path = '[{"stage":"初级云运维","goal":"云资源日常管理","salary":"10-18K","timeline":"0-2年"},{"stage":"中级云工程师","goal":"云平台架构设计","salary":"18-35K","timeline":"2-5年"},{"stage":"高级云架构师","goal":"多云混合架构","salary":"35-60K","timeline":"5-8年"},{"stage":"云技术总监","goal":"云原生战略","salary":"60K+","timeline":"8年+"}]',
  transition_to = '[1, 7]'
WHERE id = 8;

UPDATE job_categories SET
  description = '移动端开发工程师负责iOS和Android平台原生应用的开发与维护。工作包括UI组件开发、性能优化、第三方SDK集成、跨平台方案探索。需要精通Swift/Kotlin或Flutter/React Native等跨平台框架，了解移动端架构模式（MVVM/MVP），熟悉App发布流程。',
  core_skills = '["Swift/Kotlin", "Flutter/React Native", "MVVM/MVP", "性能优化", "第三方SDK", "App发布", "原生控件", "跨平台"]',
  promotion_path = '[{"stage":"初级移动开发","goal":"独立完成功能模块","salary":"8-15K","timeline":"0-2年"},{"stage":"中级移动开发","goal":"核心模块与性能优化","salary":"15-28K","timeline":"2-5年"},{"stage":"高级移动开发","goal":"架构设计与技术选型","salary":"28-45K","timeline":"5-8年"},{"stage":"移动端架构师","goal":"终端技术战略","salary":"45K+","timeline":"8年+"}]',
  transition_to = '[2, 1]'
WHERE id = 9;

UPDATE job_categories SET
  description = '测试开发工程师负责软件质量保障和自动化测试体系搭建。工作包括编写测试计划与用例、开发自动化测试框架、集成CI/CD测试流程、性能测试与安全测试。需要至少熟悉一种编程语言用于测试脚本开发，掌握主流测试工具和测试方法论。',
  core_skills = '["Python/Java", "Selenium/Appium", "自动化框架", "CI/CD", "性能测试", "测试方法论", "Bug管理", "接口测试"]',
  promotion_path = '[{"stage":"初级测试工程师","goal":"编写测试用例与手工测试","salary":"6-12K","timeline":"0-2年"},{"stage":"测试开发工程师","goal":"自动化测试框架开发","salary":"12-22K","timeline":"2-4年"},{"stage":"高级测试开发","goal":"质量体系搭建","salary":"22-35K","timeline":"4-7年"},{"stage":"质量总监","goal":"质量战略与团队","salary":"35K+","timeline":"7年+"}]',
  transition_to = '[1, 8]'
WHERE id = 10;
