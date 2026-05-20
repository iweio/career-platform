# 职业规划智能体 (CareerPlanningAgent)

## 一、功能概述

职业规划智能体基于用户的匹配分析结果，为用户提供未来5年的职业发展预测和规划路径。

### 核心功能

1. **薪资趋势预测** - 预测目标岗位2026-2030年的薪资潜力
2. **需求趋势预测** - 预测目标岗位2026-2030年的市场需求趋势
3. **职业发展路径** - 结合用户画像生成清晰的晋升/转岗路径

---

## 二、技术架构

### 技术栈

- Python 3.10+
- LangChain v1.x + LangGraph
- DeepSeek 大模型
- SQLAlchemy (数据库连接)
- matplotlib (数据可视化)
- pydantic (结构化输出)

### Agent 架构

```
CareerPlanningAgent
├── Tools
│   ├── get_top_matched_job()     # 从数据库获取匹配度最高的岗位
│   ├── predict_trends()          # DeepSeek预测薪资/需求趋势
│   └── generate_career_path()    # DeepSeek生成分阶段职业路径
└── Output
    ├── salary_demand_json        # 结构化JSON (薪资/需求/年份)
    └── career_path_json          # 分阶段路径JSON
```

---

## 三、数据来源

### 数据库5: 匹配分析报告表 (matching_report)

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | INT | 用户ID |
| job_name | VARCHAR | 岗位名称 |
| match_score | FLOAT | 匹配分数 |
| industry | VARCHAR | 行业 |
| city | VARCHAR | 城市 |
| publish_date | DATE | 发布日期 |

### 数据库3: 岗位晋升和换岗路径表 (promotion_transition)

| 字段 | 类型 | 说明 |
|------|------|------|
| job_id | INT | 岗位ID |
| current_role | VARCHAR | 当前角色 |
| next_role | VARCHAR | 下一角色 |
| required_skills | TEXT | 所需技能 |
| transition_type | ENUM | 晋升/转岗 |
| years_exp | INT | 所需年限 |

### 用户画像参数

```python
{
    "education": "本科",
    "major": "计算机",
    "skills": ["Python", "AI", "数据分析"],
    "experience": "3年",
    "city": "杭州",
    "target_salary": 30000,
    "preference": "技术专家路线"
}
```

---

## 四、输出示例

### 1. 薪资与需求趋势 (JSON)

```json
{
    "job_name": "Java开发工程师",
    "years": [2026, 2027, 2028, 2029, 2030],
    "salary": [18000, 21000, 25000, 30000, 35000],
    "salary_unit": "CNY/月",
    "demand": [65, 72, 80, 85, 90],
    "demand_unit": "指数(0-100)"
}
```

### 2. 职业发展路径

```json
{
    "current": "Java开发工程师",
    "target": "技术专家/架构师",
    "phases": [
        {
            "阶段": "第一阶段(2026-2027)",
            "目标": "中级Java开发",
            "能力要求": ["Spring Boot高级", "微服务", "数据库优化"],
            "薪资预期": "20-25K"
        },
        {
            "阶段": "第二阶段(2028-2029)",
            "目标": "高级Java开发/技术负责人",
            "能力要求": ["架构设计", "团队管理", "技术选型"],
            "薪资预期": "30-40K"
        },
        {
            "阶段": "第三阶段(2030+)",
            "目标": "技术专家/架构师",
            "能力要求": ["系统性思考", "跨团队协作", "技术战略"],
            "薪资预期": "50K+"
        }
    ]
}
```

---

## 五、使用方法

### 1. 环境配置

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DATABASE_URL3=mysql+pymysql://user:pass@host:3306/db3
DATABASE_URL5=mysql+pymysql://user:pass@host:3306/db5
```

### 3. 运行示例

```python
from agents.career_planner.agent import CareerPlanningAgent

agent = CareerPlanningAgent()
user_profile = {
    "education": "本科",
    "major": "计算机",
    "skills": ["Python", "AI"],
    "experience": "3年",
    "city": "杭州"
}

# 获取职业规划
result = agent.run(user_id=999)
```

---

## 六、API 接口

### POST /api/career_plan

**请求参数:**
```json
{
    "user_id": 999
}
```

**返回示例:**
```json
{
    "success": true,
    "top_job": "Java开发工程师",
    "match_score": 82.5,
    "trends": {
        "salary": [18000, 21000, 25000, 30000, 35000],
        "demand": [65, 72, 80, 85, 90],
        "years": [2026, 2027, 2028, 2029, 2030]
    },
    "career_path": {
        "phases": [...]
    },
    "chart_path": "/static/career_trends.png"
}
```

---

## 七、输出图表

生成的折线图包含:
- **X轴**: 年份 (2026-2030)
- **Y轴左**: 薪资 (CNY/月)
- **Y轴右**: 需求指数 (0-100)

![职业趋势图示例](chart_example.png)

---

## 八、文件结构

```
agents/career_planner/
├── agent.py              # 核心Agent类
├── tools/
│   ├── db_tools.py       # 数据库查询工具
│   └── llm_tools.py      # LLM调用工具
├── prompts/
│   └── career_prompts.py # 提示词模板
├── schemas/
│   └── career_schemas.py # Pydantic模型
├── .env.example          # 环境变量示例
└── requirements.txt      # 依赖列表
```

---

## 九、注意事项

1. 需要有效的 DeepSeek API Key
2. 数据库3和数据库5需要包含对应数据
3. 趋势预测基于当前市场情况，实际结果可能有所偏差
4. 生成的图表保存在 `static/career_trends.png`
