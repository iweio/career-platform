# SPEC — 前端重构 SSD 契约

> **目标**：将前端从静态 Mock 数据驱动 → 真实 API 驱动，所有静态资源入库。
> **原则**：先修 Bug，再搬数据，最后连线。每个 Phase 完成后 git commit。

---

## 一、API 契约 — Bug 修复与字段对齐

### 1.1 Bug #1: auth login 格式错误

**现状**：
- 前端 `auth.js:8`：`new URLSearchParams(data)` + `Content-Type: application/x-www-form-urlencoded`
- 后端 `auth.py:34`：`async def login(req: LoginRequest)` — Pydantic 期望 JSON body

**修复**：前端 `login()` 改发 JSON：
```js
login(data) {
  return api.post('/auth/login', data)
},
```

**后端正确响应**（无需改）：
```json
{"access_token": "...", "refresh_token": "...", "token_type": "bearer", "user_id": 1, "username": "testuser"}
```

---

### 1.2 Bug #2: learning plan generate 端点路径错误

**现状**：
- 前端 `learningPlan.js:5`：`POST /learning-plan`
- 后端 `learning_plan.py:34`：`POST /learning-plan/generate`

**修复**：前端改为：
```js
generate(data) {
  return api.post('/learning-plan/generate', data, { timeout: 120000 })
},
```

---

### 1.3 Bug #3: response 字段路径解包不一致

| 位置 | 前端当前写法 | 后端实际返回 | 修复写法 |
|------|-------------|-------------|---------|
| `Home.vue:417` loadHotJobs | `data.jobs` | `{success, data: {jobs, total, ...}}` | `data.data.jobs` |
| `JobExplorer.vue` loadJobs | `data.jobs` | `{success, data: {results: [...]}}` (search 模式) | `data.data.results` |
| `Home.vue:417` hotJobs | `item.job_title` / `item.title` 双写 | `item.job_title` | 统一 `item.job_title` |
| `Home.vue:420` hotJobs | `item.company_name` / `item.company` 双写 | `item.company` | 统一 `item.company` |
| `Home.vue:421` hotJobs | `item.city` | `item.city` | ✅ 正确 |
| `Home.vue:422` hotJobs | `item.match_rate` | 不存在 | 后续由 matching API 提供 |
| `Home.vue:423` hotJobs | `item.salary_range` / `item.salary` | `item.salary_range` | 统一 `item.salary_range` |
| `Home.vue:424` hotJobs | `item.industry` split | `item.industry` | ✅ 正确 |

---

### 1.4 Bug #4: JobDetail Neo4j 直连

**现状**：`JobDetail.vue` 直接 `neo4j.driver('bolt://localhost:7687', neo4j.auth.basic('', ''))`，空凭据、直连浏览器不可行。

**修复方案**：
- 新增后端端点 `GET /api/v1/jobs/{job_id}/graph` 返回 Neo4j 图数据
- 前端改为调 API

**新增 API 契约**：

| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | `/jobs/{job_id}/graph` | No | `{success, data: {nodes: [{id, name, type, group}], links: [{source, target, relation}]}}` |

---

### 1.5 Bug #5: PromotionGraph 依赖不存在的 mock 目录

**现状**：`PromotionGraph.vue` 使用 `import.meta.glob('@/mock/promotion/*.json')` 但 `src/mock/` 不存在。

**修复方案**：
- 后端 `GET /api/v1/jobs/{job_id}/promotion` 从 `promotion_transition` 表查晋升路径
- 前端改为调 API

**新增 API 契约**：

| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | `/jobs/{job_id}/promotion` | No | `{success, data: {current_role, paths: [{from, to, skills, years, type}], related_jobs: [{title, company}]}}` |

---

### 1.6 后端需补充的端点

| # | Method | Path | Auth | 说明 | 响应 data 字段 |
|---|--------|------|------|------|---------------|
| 1 | GET | `/jobs/{id}/graph` | No | Neo4j 图数据 | `{nodes, links}` |
| 2 | GET | `/jobs/{id}/promotion` | No | 晋升路径 | `{current_role, paths, related_jobs}` |
| 3 | GET | `/profile/analysis` | Yes | 用户完整分析数据 | `{competitiveness_score, radar_data, word_cloud, ai_report}` |
| 4 | GET | `/profile/tasks` | Yes | 用户每日任务 | 同 `/learning-plan/tasks`（已有） |

---

## 二、DB Schema 契约 — 静态数据入库

### 2.1 新增表：`job_categories`

前端的 10 个职业分类卡片（Home.vue 左侧面板）存入数据库。

```sql
CREATE TABLE IF NOT EXISTS job_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '分类名，如"后端开发"',
    icon VARCHAR(50) COMMENT 'Element Plus icon 名',
    tag VARCHAR(30) COMMENT '标签，如"高需求"',
    sort_order INT DEFAULT 0,
    insight_scarcity VARCHAR(30) COMMENT '稀缺度标签',
    insight_forecast TEXT COMMENT 'AI 预测文本 JSON',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**种子数据**（从 Home.vue `categories` 提取，共 10 条）：

| name | icon | tag |
|------|------|-----|
| 后端开发 | Monitor | 高需求 |
| 前端开发 | Grid | 热门 |
| AI / 机器学习 | Cpu | 新兴 |
| 数据分析 | DataAnalysis | 高薪 |
| 产品经理 | User | 管理岗 |
| UI / UX 设计 | Brush | 创意 |
| 网络安全 | Lock | 稀缺 |
| 云计算 | Cloudy | 增长快 |
| 移动端开发 | Iphone | 稳定 |
| 测试开发 | Checked | 基础岗 |

---

### 2.2 扩充 `promotion_transition` 种子数据

前端 `JobDetail.vue` 中的 `nameMap`（中英文岗位映射）覆盖了约 15 个岗位。需确保每个岗位在 `promotion_transition` 中有完整的晋升/转岗路径。

从旧后端 `carrer-Agents/init_database.sql` 补充（需读取该文件确认实际数据）。

---

### 2.3 `learning_plans` + `daily_tasks` 种子数据

前端的硬编码学习计划（`PolishAndExport.vue` 中 4 阶段 Java 计划 + `GrowthTracker.vue` 中 5 个 Java 任务）作为**默认模板**入库，用户首次使用时复制一份。

方案：新增 `plan_templates` 表存放预置模板，API `/learning-plan/templates` 返回可选模板列表。

```sql
CREATE TABLE IF NOT EXISTS plan_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) COMMENT '模板名，如"Java 高级架构师"',
    target_job VARCHAR(100),
    plan_type VARCHAR(50) DEFAULT '长期',
    phases JSON COMMENT '阶段数组',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

### 2.4 种子数据更新总结

| 表 | 操作 | 数据来源 |
|----|------|---------|
| `jobs` | 补充更多岗位（目前仅 4 条） | 前端 15 个 post sphere 节点 + 旧后端种子数据 |
| `job_categories` | **新增表** | Home.vue 10 个 category |
| `promotion_transition` | 扩充 | 旧后端 init_database.sql + 前端 nameMap |
| `plan_templates` | **新增表** | PolishAndExport.vue + GrowthTracker.vue |
| `daily_tasks` | 改为由 `/learning-plan/generate` 自动生成 | — |
| `user_profiles` | — | 由 resume_analyzer Agent 写入 |

---

## 三、前端重构契约 — Mock → API 映射

### 3.1 Home.vue

| 当前 Mock 数据 | 变量 | 替换为 | API |
|---------------|------|--------|-----|
| 10 个 categories 硬编码 | `categories` | DB 查 `job_categories` 表 | `GET /api/v1/jobs/categories` （新增） |
| `competitivenessScore = 75` | `competitivenessScore` | 从 user profile 分析结果取 | `GET /api/v1/profile/analysis` |
| `skillCompleteness = 82` | `skillCompleteness` | 从 user profile 的 completeness 字段 | 同上 |
| `hotSearchTags` 硬编码 6 个 | `hotSearchTags` | 从 DB/jobs 热门关键词取 | `GET /api/v1/jobs/hot-tags` （新增，或从 hot jobs 提取） |
| `dailyTasks` 硬编码 3 个 | `dailyTasks` | 从 learning plan 每日任务取 | `GET /api/v1/learning-plan/tasks` |
| `skillGaps` 硬编码 3 个 | `skillGaps` | 从 matching report 的 gap_analysis 取 | 由 `/matching/match` 结果中提取 |
| `shortAgentAdvice` 硬编码文本 | `shortAgentAdvice` | 从 matching report 的 summary 取 | 同上 |
| `calculateWinRate()` 公式 | — | 后端 matching 计算 | `/matching/match` |
| `calculateSalaryPremium()` | — | 后端 career_plan 计算 | `/career-plan` |
| `generateAgentDecision()` 模板文本 | — | 后端 matching Agent 生成 | `/matching/match` |
| 15 个 `post-sphere` 硬编码 | — | 从 DB jobs 表动态渲染 | `GET /api/v1/jobs?page_size=15` |
| `hotJobs` from jobsApi.list() | `hotJobs` | 已有 API，修复字段映射 | `GET /api/v1/jobs?page_size=10` |

### 3.2 Profile/Index.vue

| 当前 Mock 数据 | 替换为 | API |
|---------------|--------|-----|
| `scriptSteps` 3 步剧本 | resume_analyzer Agent 的真实追问 | `POST /api/v1/resume/extract` + `POST /api/v1/resume/supplement` |
| `currentRadarData` 硬编码 | Agent 实时分析结果 | 同上 |
| `dimensionDetails` 硬编码 | Agent 提取的 profile 维度 | 同上 |
| `chatMessages` 模拟对话 | 真实 API 对话 | resume extract/supplement 循环 |
| `quickActions` | 可保留为 UI 快捷入口 | — |
| `progressValue` | 从 Agent 返回的 completeness 取 | resume extract |

**交互逻辑重构**：
1. 用户输入/上传 → `POST /resume/extract` → Agent 返回 `{profile_data, completeness, question?}`
2. 如果有 `question`（追问） → 显示追问 → 用户回答 → `POST /resume/supplement`
3. 重复直到完整 → 显示 "分析完成"
4. 用户点"保存并开始 AI 深度分析" → `POST /resume/analyze` → 跳转 PersonalInfo 视图

### 3.3 Profile/PersonalInfo.vue

| 当前 Mock 数据 | 替换为 | API |
|---------------|--------|-----|
| `competitivenessScore = 88` | Agent 分析结果 | `GET /api/v1/profile/analysis` |
| 雷达图数据 `[85,90,95,95,80,85,60]` | Agent 分析结果 | 同上 |
| 词云数据 | Agent 分析结果或从 user_profiles 提取 | 同上 |
| 3 段 AI 报告文本 | Agent 生成的 `analysis_report` | 同上 |
| `displayPercentage = 85` | user_profile.completeness | 同上 |

### 3.4 Profile/AIReport.vue

| 当前 Mock 数据 | 替换为 | API |
|---------------|--------|-----|
| `overallScore = 89.62` | matching report | `POST /api/v1/matching/match` |
| `aiSummary` 长文本 | matching report summary | 同上 |
| `skillDetails` 7 维度分数+评论 | matching report dimension_scores | 同上 |
| `expectedCities` 3 城市 | career plan top cities | `POST /api/v1/career-plan` |
| `salaryForecast` 5 年 | career plan salary trends | 同上 |
| `jobDemandTrend` 5 年 | career plan demand trends | 同上 |
| `chart_url` | career plan 生成的图（matplotlib） | 同上 |

### 3.5 Profile/GrowthTracker.vue

| 当前 Mock 数据 | 替换为 | API |
|---------------|--------|-----|
| `todoList` 5 个 Java 任务 | 从 learning plan daily tasks 取 | `GET /api/v1/learning-plan/tasks` |
| 雷达图当前值 vs 目标值 | user profile + matching report gap | `/profile/analysis` + `/matching/match` |
| `aiAnalysis` 文本 | learning plan Agent 建议 | `/learning-plan/generate` 的 summary |
| `targetPosition = 'Java'` | user profile 中的目标岗位 | `/profile/analysis` |
| `consecutiveDays = 12` | 从 daily_tasks 完成记录计算 | 后端计算 |
| 职业路径 steps | career plan career_path | `/career-plan` |
| 浮动智能辅导对话 | 实时调用 resume Agent | `/resume/extract` |

### 3.6 Profile/PolishAndExport.vue

| 当前 Mock 数据 | 替换为 | API |
|---------------|--------|-----|
| 4 阶段 Java 学习计划 | Agent 生成的 learning plan | `GET /api/v1/learning-plan/generate` + `/tasks` |
| `handleAIPolish` 模拟润色 | 真实 AI 润色 | `POST /api/v1/learning-plan/polish` |
| `polishHistory` | 存后端或 localStorage（增强：存 DB） | `/learning-plan/polish` 历史可由后端维护 |
| PDF 导出 | 保持前端 html2pdf，改用真实数据 | — |

### 3.7 JobDetail.vue

| 当前 Mock 数据 | 替换为 | API |
|---------------|--------|-----|
| Neo4j 直连图（`force-graph`） | 后端返回图数据 | `GET /api/v1/jobs/{id}/graph` |
| `PromotionGraph` mock JSON | 后端 promotion_transition 数据 | `GET /api/v1/jobs/{id}/promotion` |
| `nameMap` 硬编码映射 | 后端直接返回中文名 | 同上 |
| 岗位基本信息 | 已有 API | `GET /api/v1/jobs/{id}` ✅ |
| 收藏操作 | 已有 API | `POST/DELETE /api/v1/favorites` ✅ |

### 3.8 PromotionGraph.vue

- **删除** `import.meta.glob('@/mock/promotion/*.json')`
- 改为接收 prop `promotionData`（由父组件从 API 获取后传入）
- 组件变为纯渲染组件

### 3.9 JobExplorer.vue

- 已有 API 集成（`jobsApi.search()` / `jobsApi.list()`）
- 修复字段映射：`data.data.results` 或 `data.data.jobs`
- 筛选选项（行业、薪资、经验、城市）目前硬编码 → 后续可从 `/jobs/filters` API 动态获取

---

## 四、后端新增端点汇总

| # | Method | Path | Auth | 响应 data 字段 |
|---|--------|------|------|---------------|
| 1 | GET | `/jobs/categories` | No | `[{id, name, icon, tag, scarcity, forecast}]` |
| 2 | GET | `/jobs/hot-tags` | No | `["前端开发", "AI算法", ...]` |
| 3 | GET | `/jobs/{id}/graph` | No | `{nodes: [{id,name,type,group}], links: [{source,target,relation}]}` |
| 4 | GET | `/jobs/{id}/promotion` | No | `{current_role, paths: [{from,to,skills,years,type}], related_jobs: [...]}` |
| 5 | GET | `/profile/analysis` | Yes | `{competitiveness_score, radar_data: [...], word_cloud: [...], ai_report: {advantages, suggestions, outlook}}` |

---

## 五、文件改动清单

### Phase 1: 修 Bug（5 文件）

| 文件 | 改动 |
|------|------|
| `career-front-main/src/api/auth.js` | login() 改为 JSON，删 URLSearchParams |
| `career-front-main/src/api/learningPlan.js` | generate() 端点改为 `/learning-plan/generate` |
| `career-front-main/src/views/Home.vue` | loadHotJobs() 解包路径修正：`data.data.jobs` |
| `career-front-main/src/views/Jobs/JobExplorer.vue` | 响应解包修正：`data.data.results` / `data.data.jobs` |
| `career-front-main/src/views/Jobs/JobDetail.vue` | 删 Neo4j 直连，改用 API |

### Phase 2: DB 种子数据（3 文件）

| 文件 | 改动 |
|------|------|
| `backend/scripts/init_db.sql` | 新增 `job_categories` 建表 + 10 条种子；新增 `plan_templates` 建表 + 1 条种子 |
| `backend/app/models/` | 新增 `job_category.py` + `plan_template.py` ORM 模型 |
| `backend/app/api/v1/jobs.py` | 新增 `/categories` `/hot-tags` `/{id}/graph` `/{id}/promotion` 端点 |

### Phase 3: 前端连线（8+ 文件）

| 文件 | 改动 |
|------|------|
| `Home.vue` | categories/matching/tasks 全部接 API |
| `Profile/Index.vue` | scriptSteps → resume API 交互循环 |
| `Profile/PersonalInfo.vue` | 硬编码 → `/profile/analysis` |
| `Profile/AIReport.vue` | mockFetchData → matching + career-plan API |
| `Profile/GrowthTracker.vue` | 硬编码 → learning-plan tasks + matching gap |
| `Profile/PolishAndExport.vue` | 硬编码计划 → learning-plan generate/polish |
| `Profile/FavoriteJobs.vue` | ✅ 已 API 集成（确认字段路径） |
| `components/PromotionGraph.vue` | `import.meta.glob` → props 接收 |
| `components/RadarChart.vue` | ✅ 纯组件，无需改 |

---
---
## 六、简历向量化入库 RAG — 规约

> **触发**：用户要求"把简历向量化放到 RAG 里"。
> **日期**：2026-05-22

### 6.1 ChromaDB Schema 契约

| 属性 | 值 |
|------|-----|
| Collection 名 | `user_resumes`（config: `CHROMA_COLLECTION_RESUMES`）|
| 距离度量 | cosine |
| 主键 | `user_id`（存为 ChromaDB document id）|
| 文档内容 | 结构化 profile 文本（`_profile_to_text` 转换） |
| 元数据 | `name: str`，`top_skills: str`（逗号分隔） |
| 写入策略 | upsert（先 `collection.delete(ids=[user_id])` 再 `collection.add`）|

### 6.2 入库时机契约

| 端点 | 条件 | 行为 |
|------|------|------|
| `POST /resume/extract` | agent 返回且 `user_profile` 非空 | 调用 `_store_resume_vector(user_id, user_profile)` |
| `POST /resume/supplement` | 同上 | 同上 |
| `POST /resume/analyze` | 同上 | 同上 |

- ChromaDB 写入失败 → 只打日志，不抛异常，不影响 API 响应
- `user_profile` 为空 → 直接跳过

### 6.3 匹配消费契约

`job_matcher/nodes.py` → `retrieve_candidates` 节点：
1. 调用 `resume_retriever.get_vector(user_id)` 取已存简历文本
2. 取到 → 用自然语言格式文本做向量检索（嵌入质量优于 JSON）
3. 取不到 → 回退 `json.dumps(profile)`（原逻辑不变）

### 6.4 改动文件

| 文件 | 改动 | 说明 |
|------|------|------|
| `app/config.py` | +1 行 | `CHROMA_COLLECTION_RESUMES` |
| `app/rag/vector_store.py` | +`get_resume_collection()` | 新增 collection，`reset_collections` 多清一个 |
| `app/rag/retrievers.py` | +`ResumeRetriever` 类 | `store/search/get_vector/delete` |
| `app/api/v1/resume.py` | +3 个 helper + 3 行调用 | `_profile_to_text`, `_extract_name`, `_extract_skills`, `_store_resume_vector` |
| `app/agents/job_matcher/nodes.py` | +2 行 | 优先取已存向量 |

### 6.5 验证清单

- [x] resume extract → ChromaDB `user_resumes` 有记录
- [x] `resume_retriever.search("Python 后端")` 可命中
- [ ] matching 使用已存向量 → 匹配质量对比
- [ ] resume 更新 → ChromaDB 刷新（upsert 验证）

---
---
---
---
## 七、大岗位族匹配 + Neo4j 建图 + 3 Bug 修复 — 规约

> **日期**：2026-05-22
> **触发**：用户指出匹配逻辑应对 10 大岗位族做语义匹配，非 15 小岗位；且发现 4 库 4 断裂点。

### 7.1 API 契约

无新增/删改端点。变更如下：

#### 7.1.1 Matching 流程变更

```
旧：简历文本 → ChromaDB.job_descriptions(15小岗位) → top-N 小岗位
新：简历文本 → ChromaDB.job_categories(10大岗位族) → top-N 岗位族 → MySQL.jobs WHERE category_id IN (...)
```

- `POST /matching/match` 返回字段不变：`{success, data: {matches: [{job_title, company, match_score, ...}]}}`
- 内部 RAG 命中 10 大岗位族后，从 MySQL `jobs` 表捞对应 category 的岗位

#### 7.1.2 职类搜索增强

- `GET /api/v1/jobs/search?q=后端` → ChromaDB 搜大岗位族 → 返回 MySQL 中该族下的具体职位
- 逻辑同 matching，但不需要用户简历

### 7.2 DB Schema 契约

#### 7.2.1 MySQL: `jobs` 表加 `category_id`

```sql
ALTER TABLE jobs ADD COLUMN category_id INT REFERENCES job_categories(id);
```

映射关系：

| job_id | job_title | category_id |
|--------|-----------|-------------|
| 1 | Python后端开发工程师 | 1 (后端开发) |
| 2 | 前端开发工程师 | 2 (前端开发) |
| 3 | 数据分析师 | 4 (数据分析) |
| 4 | 产品经理 | 5 (产品经理) |
| 5 | AI算法工程师 | 3 (AI/机器学习) |
| 6 | 网络安全工程师 | 7 (网络安全) |
| 7 | UI/UX设计师 | 6 (UI/UX设计) |
| 8 | 云计算架构师 | 8 (云计算) |
| 9 | 移动端开发工程师 | 9 (移动端开发) |
| 10 | 测试开发工程师 | 10 (测试开发) |
| 11 | 全栈开发工程师 | 1 (后端开发) |
| 12 | 运维SRE工程师 | 8 (云计算) |
| 13 | 游戏开发工程师 | 9 (移动端开发) |
| 14 | 物联网工程师 | 9 (移动端开发) |
| 15 | 交互设计师 | 6 (UI/UX设计) |

#### 7.2.2 MySQL: `job_categories` 表加字段

```sql
ALTER TABLE job_categories ADD COLUMN description TEXT COMMENT '岗位族描述，用于向量化';
ALTER TABLE job_categories ADD COLUMN core_skills JSON COMMENT '核心技能列表';
ALTER TABLE job_categories ADD COLUMN promotion_path JSON COMMENT '晋升路径，入Neo4j';
ALTER TABLE job_categories ADD COLUMN transition_to JSON COMMENT '可转岗方向';
```

#### 7.2.3 ChromaDB: `job_descriptions` → `job_categories`

- 旧：15 docs，每个为具体职位文本
- 新：10 docs，每个为岗位族描述文本（从 `job_categories.description`）
- Collection 名改为 `job_categories`（config: `CHROMA_COLLECTION_JOBS` 值改为 `job_categories`）

#### 7.2.4 Neo4j: 职位晋升图谱

节点标签：`Category`（10 个岗位族）

```
(:Category {name: "后端开发"})
  -[:PROMOTES_TO {years: "3-5年"}]-> (:Category {name: "后端开发"})
  -[:TRANSITIONS_TO]-> (:Category {name: "云计算"})
  -[:TRANSITIONS_TO]-> (:Category {name: "AI/机器学习"})
```

### 7.3 Bug 修复契约

#### 7.3.1 `user_profiles` 不写库

- **根因**：resume agent `generate_report` 节点只把数据存入 state，未写 MySQL
- **修复**：agent 的 `generate_report` 节点中，`db_utils.save_user_profile()` 原本不存在 → 新增，在 `analyze_profile` 完成后写库
- **API 层备选**：`resume.py` 的 `_store_resume_vector` 同时写 MySQL `user_profiles` 表

#### 7.3.2 `career_plans` 不写库

- **根因**：career_planner 的 `save_plan` 节点依赖 `db_utils.save_career_plan()` → 检查是否存在
- **修复**：确认 `db_utils.save_career_plan` 被正确调用，目标表 `career_plans` 的 `plan_data` JSON 列接收完整 plan

#### 7.3.3 `daily_tasks` 不写库

- **根因**：learning_plan agent 的 `daily_tasks` 节点不持久化
- **修复**：在 `daily_tasks` 节点中调用 `tools.save_daily_tasks()` 写入 `daily_tasks` 表

### 7.4 改动文件

| 文件 | 改动 |
|------|------|
| `app/config.py` | `CHROMA_COLLECTION_JOBS` 值改为 `job_categories` |
| `app/models/job.py` | `Job` 模型加 `category_id` |
| `app/models/job_category.py` | 加 `description`, `core_skills`, `promotion_path`, `transition_to` |
| `scripts/init_db.sql` | `jobs` 加 `category_id`；`job_categories` 加 4 列 + 10 条种子数据 |
| `app/rag/ingest_jobs.py` | 改为从 `job_categories` 读描述 → 向量化入库 |
| `app/rag/ingest_neo4j.py` | **新增**：启动时将 `job_categories.promotion_path` 入 Neo4j |
| `app/agents/job_matcher/nodes.py` | `retrieve_candidates` 从 10 族命中 → 回 MySQL 捞职位 |
| `app/agents/resume_analyzer/nodes.py` | `generate_report` 加写 `user_profiles` |
| `app/agents/career_planner/nodes.py` | `save_plan` 加写 `career_plans` |
| `app/agents/learning_plan/nodes.py` | `generate_daily_tasks` 加写 `daily_tasks` |
| `app/main.py` | lifespan 加 `ingest_neo4j` 调用 |

### 7.5 种子数据契约（用户提供）

10 大岗位族，每个需提供：

| 字段 | 用途 | 字数 |
|------|------|------|
| `description` | ChromaDB 向量化，语义匹配 | ~200 字 |
| `core_skills` | 匹配维度评分参考 | 8-12 个 |
| `promotion_path` | Neo4j 图谱：`[{stage, goal, requirements, salary, timeline}]` | 4 级 |
| `transition_to` | Neo4j 图谱：可转岗的 category_id 列表 | 2-3 个 |

### 7.6 构建契约

```bash
cd backend && docker compose build backend && docker compose up -d backend
```

ChromaDB 启动时自动 `reset_collections` → 重新从 `job_categories` ingest 10 条。
Neo4j 启动时自动建图。

### 7.7 验证清单

- [ ] MySQL `jobs` 有 `category_id` 列，15 行全部非 NULL
- [ ] MySQL `job_categories` 有完整 10 条种子数据（含 description）
- [ ] ChromaDB `job_categories` 有 10 条 DashScope 向量
- [ ] Neo4j 有 10 个 `Category` 节点 + PROMOTES_TO + TRANSITIONS_TO 边
- [ ] `POST /resume/extract` → MySQL `user_profiles` 有数据
- [ ] `POST /career-plan` → MySQL `career_plans` 有数据
- [ ] `POST /learning-plan/daily-tasks` → MySQL `daily_tasks` 有数据
- [ ] `POST /matching/match` → 返回岗位族对应职位，非孤立的 15 小岗位
- [ ] RAG 搜索 "后端开发" → 返回 category 1 下的 2 个职位

---
---
### Phase 4: 构建验证

```bash
cd career-front-main && npm run build
docker compose up -d --build
# 验证: curl http://localhost:8000/api/v1/jobs/categories
```
