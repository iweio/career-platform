# 人岗匹配智能体 (Job Matcher Agent)

## 简介

人岗匹配智能体是一个基于 LangChain 和大语言模型(LLM)的智能招聘匹配系统。该智能体通过分析用户的职业画像与岗位要求，计算匹配分数并生成详细的差距报告，帮助用户了解与目标岗位的匹配程度。

## 核心功能

### 1. 权重分析
根据岗位详情和公司描述，使用 LLM 分析该岗位对以下7个维度的重视程度：
- 专业技能：技术能力、专业知识
- 证书：相关资质证书
- 创新能力：创新思维、问题解决能力
- 学习能力：学习速度、知识吸收能力
- 抗压能力：压力管理、危机处理
- 沟通能力：团队协作、表达沟通
- 实习能力：实践经验、项目经验

### 2. 人岗匹配评分
对比用户画像和岗位要求，对每个维度进行评分（0-100分）：
- 90-100分：完全匹配或超出要求
- 70-89分：基本匹配，有少量差距
- 50-69分：部分匹配，有明显差距
- 30-49分：差距较大
- 0-29分：严重不匹配

### 3. 差距报告生成
生成详细的差距报告，包含：
- 各维度得分和权重
- 与目标公司要求的差距
- 与行业普遍要求的差距
- 综合匹配分数

## 技术架构

### 核心技术栈
- **LangChain**: LLM 应用开发框架
- **LangChain OpenAI**: OpenAI/DeepSeek 模型集成
- **FastAPI**: API 服务框架
- **Pymysql**: MySQL 数据库连接
- **Neo4j**: 图数据库存储岗位画像
- **Docker**: 容器化部署

### 项目结构
```
job_matcher/
├── __init__.py       # 入口文件，导出 run_workflow
├── match_agent.py    # 核心匹配逻辑
├── db_utils.py       # 数据库工具函数（使用 pymysql）
├── config.py         # 配置管理
└── README.md         # 本文档
```

## 数据库结构

### MySQL 表

#### user_profiles（用户画像表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| user_id | INT | 用户ID（唯一） |
| profile_data | JSON | 用户画像数据（7个维度） |
| match_score | FLOAT | 匹配分数 |
| status | VARCHAR | 状态 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### jobs（岗位表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| title | VARCHAR | 岗位标题 |
| company | VARCHAR | 公司名称 |
| city | VARCHAR | 城市 |
| min_salary | INT | 最低薪资 |
| max_salary | INT | 最高薪资 |
| description | TEXT | 岗位描述 |
| company_description | TEXT | 公司描述 |

#### favorites（收藏表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| user_id | INT | 用户ID |
| job_id | INT | 岗位ID |
| created_at | DATETIME | 创建时间 |

### Neo4j 图结构

#### JobProfile 节点
存储岗位的标准画像，包含7个维度的期望值：
- 专业技能
- 证书
- 创新能力
- 学习能力
- 抗压能力
- 沟通能力
- 实习能力

## API 接口

### POST /api/match

人岗匹配接口

**请求参数**:
```json
{
  "user_id": 2
}
```

**成功响应**:
```json
{
  "success": true,
  "result": {
    "user_id": 2,
    "match_results": [
      {
        "job_id": 1,
        "job_title": "Java",
        "final_score": 69.0,
        "detail_score": 88.0,
        "profile_score": 50.0,
        "best_match_detail": {
          "job_id": 1,
          "job_title": "Java",
          "weights": {"专业技能": 0.35, "证书": 0.05, ...},
          "merged_result": {
            "专业技能": {"score": 67.5, "detail_score": 85, "profile_score": 50, "gap": "..."},
            "证书": {"score": 65.0, "detail_score": 80, "profile_score": 50, "gap": "..."},
            ...
          },
          "total_score": 69.0
        }
      },
      ...
    ],
    "best_match": {
      "job_id": 1,
      "job_title": "Java",
      "final_score": 69.0
    }
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "未找到用户 2 的画像数据"
}
```

## 使用流程

1. **数据准备**
   - 用户画像数据存入 MySQL `user_profiles` 表
   - 岗位数据存入 MySQL `jobs` 表
   - 用户收藏岗位存入 `favorites` 表
   - （可选）岗位画像存入 Neo4j `JobProfile` 节点

2. **调用匹配**:
   ```python
   from agents.job_matcher import run_workflow

   result = run_workflow({"user_id": 2})
   if result["success"]:
       match_results = result["result"]["match_results"]
       best_match = result["result"]["best_match"]
   ```

3. **结果展示**
   - 返回匹配结果列表（按分数排序）
   - 返回最佳匹配岗位及详细差距报告

## 配置说明

环境变量配置（`.env`）：
```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
MYSQL_HOST=backend-mysql-1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=job_db
NEO4J_URI=bolt://backend-neo4j-1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
MAX_CONCURRENT_MATCHES=5
```

## 前端集成

前端可通过以下步骤集成：

1. 调用 `/api/match` 接口
2. 解析返回的匹配结果
3. 展示匹配列表和详细分析

示例 JavaScript 代码：
```javascript
async function runMatcher(userId) {
    const res = await fetch('/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    });
    const data = await res.json();
    if (data.success) {
        showMatcherResult(data.result);
    }
}
```

## 匹配流程图

```
run_match(user_id)
         │
         ▼
 ┌───────────────────┐
 │ 读取用户画像      │ ← MySQL 数据库
 │ get_user_profile  │
 └───────────────────┘
         │
         ▼
 ┌───────────────────┐
 │ 读取收藏岗位列表  │ ← MySQL 数据库
 │ get_user_favorite │
 └───────────────────┘
         │
         ▼
 ┌───────────────────────────────────────────────────────┐
 │              并发处理每个岗位                          │
 │  ┌─────────────────────────────────────────────────┐  │
 │  │           _match_single_job()                    │  │
 │  │                     │                            │  │
 │  │  ┌──────────────────┼──────────────────┐        │  │
 │  │  ▼                  ▼                  ▼        │  │
 │  │ 确定权重      获取岗位详情      获取岗位画像     │  │
 │  │ (大模型)      (MySQL DB)      (Neo4j)          │  │
 │  │  │                  │                  │        │  │
 │  │  └──────────────────┼──────────────────┘        │  │
 │  │                     ▼                            │  │
 │  │         计算具体岗位匹配分                         │  │
 │  │         计算岗位画像匹配分                         │  │
 │  │                     │                            │  │
 │  │                     ▼                            │  │
 │  │           融合差距报告                           │  │
 │  └─────────────────────────────────────────────────┘  │
 └───────────────────────────────────────────────────────┘
         │
         ▼
 ┌───────────────────┐
 │ 按总分排序        │
 │ 选出最高分岗位    │
 └───────────────────┘
         │
         ▼
 ┌───────────────────┐
 │ 保存匹配报告      │ → MySQL 数据库
 │ save_match_report │
 └───────────────────┘
```

## 匹配示例

用户画像（user_id=2）包含：
- 专业技能：Python, Java, 机器学习, Spring Boot
- 证书：英语六级、计算机二级、AWS认证
- 创新能力：大学生创新创业大赛国家级立项、软件著作权1项
- 学习能力：GPA 3.8/4.0、校级奖学金3次
- 抗压能力：同时准备秋招和论文
- 沟通能力：社团联合会部长、组织多场活动
- 实习能力：字节跳动后端实习6个月、参与核心项目

**匹配结果（Java 岗位 69分）**：
- 专业技能 67.5分：用户已掌握Java、Spring Boot等后端技术，与岗位核心要求高度匹配
- 证书 65分：AWS认证对云服务开发有助力，计算机二级与英语六级符合基础要求

## 注意事项

1. **Neo4j 可选**：如果不使用 Neo4j 岗位画像，系统会使用默认权重和岗位详情进行匹配
2. **LLM 调用**：每次匹配会调用 LLM 分析权重，建议添加缓存机制
3. **并发控制**：通过 `MAX_CONCURRENT_MATCHES` 配置并发匹配数量
4. **数据库连接**：确保 MySQL 和 Neo4j 服务正常运行
5. **字符集**：MySQL 连接使用 `utf8mb4` 字符集以支持中文