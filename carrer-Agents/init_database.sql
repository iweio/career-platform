-- 数据库初始化脚本
-- 包含所有必要的表结构和初始数据

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建岗位表
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建职业规划表
CREATE TABLE IF NOT EXISTS career_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    target_position VARCHAR(255) NOT NULL,
    target_company VARCHAR(255),
    timeline_months INT,
    status VARCHAR(50) DEFAULT 'active',
    plan_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建岗位画像表
CREATE TABLE IF NOT EXISTS job_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    profile_data JSON,
    summary TEXT,
    core_skills JSON,
    career_path JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建晋升路径表
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

-- 创建人岗匹配报告表
CREATE TABLE IF NOT EXISTS matching_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_name VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    city VARCHAR(255),
    match_score DECIMAL(5,2),
    publish_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建学习任务表
CREATE TABLE IF NOT EXISTS learning_tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    task_date DATE NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    task_content TEXT NOT NULL,
    estimated_time VARCHAR(50),
    completed BOOLEAN DEFAULT FALSE,
    resources JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入初始数据
-- 插入用户数据
INSERT IGNORE INTO users (username, email, password) VALUES
('testuser', 'test@example.com', 'password123');

-- 插入岗位数据
INSERT IGNORE INTO jobs (job_title, company, industry, city, salary_range, job_description, requirements, publish_date) VALUES
('Python Backend Developer', 'Tech Company A', 'Technology', 'Beijing', '20k-30k', 'Responsible for backend development', 'Proficient in Python, Django/Flask', '2026-01-01'),
('Frontend Developer', 'Tech Company B', 'Technology', 'Shanghai', '18k-28k', 'Responsible for frontend development', 'Proficient in React, Vue', '2026-01-02'),
('Data Analyst', 'Tech Company C', 'Technology', 'Guangzhou', '15k-25k', 'Responsible for data analysis', 'Proficient in SQL, Python', '2026-01-03'),
('Product Manager', 'Tech Company D', 'Technology', 'Shenzhen', '25k-35k', 'Responsible for product management', 'Experience in product planning', '2026-01-04');

-- 插入晋升路径数据
INSERT IGNORE INTO promotion_transition (current_role, next_role, required_skills, years_exp, transition_type) VALUES
('Python Backend Dev', 'Senior Backend Engineer', '{"skills": ["System design", "Team management"]}', 3, 'promotion'),
('Python Backend Dev', 'Tech Lead', '{"skills": ["Architecture design", "Technical planning"]}', 5, 'promotion'),
('Java Developer', 'Senior Java Engineer', '{"skills": ["Microservices", "Performance optimization"]}', 3, 'promotion'),
('Frontend Developer', 'Senior Frontend Engineer', '{"skills": ["Frontend architecture", "Performance optimization"]}', 3, 'promotion'),
('Data Analyst', 'Senior Data Analyst', '{"skills": ["Machine learning", "Data modeling"]}', 3, 'promotion'),
('Product Manager', 'Senior Product Manager', '{"skills": ["Strategic planning", "Cross-team collaboration"]}', 3, 'promotion');

-- 查看所有表
SHOW TABLES;

-- 查看初始数据
SELECT 'Users' as TableName, COUNT(*) as Count FROM users UNION
SELECT 'Jobs' as TableName, COUNT(*) as Count FROM jobs UNION
SELECT 'Promotion_Transition' as TableName, COUNT(*) as Count FROM promotion_transition;