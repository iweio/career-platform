import os
import json
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

_dotenv_path = Path(__file__).parent.parent / ".env"
if _dotenv_path.exists():
    with open(_dotenv_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from .schemas.learning_schemas import LearningPlan, DailyTask, PlanGenerationRequest
from .tools.db_tools import get_user_profile, get_target_job, save_learning_plan, get_learning_plan, save_daily_tasks, update_task_status
from .prompts.learning_prompts import (
    PLAN_GENERATION_SYSTEM, PLAN_GENERATION_USER,
    DAILY_TASK_SYSTEM, DAILY_TASK_USER,
    PLAN_POLISH_SYSTEM, PLAN_POLISH_USER,
    TASK_ADJUST_SYSTEM, TASK_ADJUST_USER
)


class LearningPlanAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
            model=os.getenv("OPENAI_MODEL", "deepseek-chat"),
            temperature=0.7
        )

    def generate_plan(self, user_id: int, plan_type: str = "长期") -> Dict[str, Any]:
        user_profile = get_user_profile(user_id)
        target_job = get_target_job(user_id)

        if not target_job:
            return {"success": False, "error": "未找到目标岗位，请先完成人岗匹配"}

        user_msg = PLAN_GENERATION_USER.format(
            user_profile=json.dumps(user_profile, cls=DecimalEncoder, ensure_ascii=False, indent=2),
            target_job=json.dumps(target_job, cls=DecimalEncoder, ensure_ascii=False, indent=2),
            plan_type=plan_type
        )

        response = self.llm.invoke([
            ("system", PLAN_GENERATION_SYSTEM),
            ("human", user_msg)
        ])

        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        try:
            result = json.loads(content.strip())
        except json.JSONDecodeError:
            return {"success": False, "error": f"JSON解析失败: {content[:200]}"}

        plan = LearningPlan(
            user_id=user_id,
            target_job=target_job.get("job_title", ""),
            plan_type=plan_type,
            phases=result.get("phases", []),
            raw_response=content
        )

        save_learning_plan(plan)

        return {
            "success": True,
            "plan": plan.to_dict()
        }

    def polish_plan(self, current_plan: Dict[str, Any], user_feedback: str) -> Dict[str, Any]:
        user_msg = PLAN_POLISH_USER.format(
            current_plan=json.dumps(current_plan, cls=DecimalEncoder, ensure_ascii=False, indent=2),
            user_feedback=user_feedback
        )

        response = self.llm.invoke([
            ("system", PLAN_POLISH_SYSTEM),
            ("human", user_msg)
        ])

        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        try:
            result = json.loads(content.strip())
        except json.JSONDecodeError:
            return {"success": False, "error": f"JSON解析失败: {content[:200]}"}

        return {
            "success": True,
            "polished_plan": result
        }

    def generate_daily_tasks(self, user_id: int, phase_index: int = 0) -> Dict[str, Any]:
        user_profile = get_user_profile(user_id)
        target_job = get_target_job(user_id)
        plan_data = get_learning_plan(user_id)

        if not plan_data:
            return {"success": False, "error": "未找到学习计划"}

        phases = plan_data.get("phases", [])
        if phase_index >= len(phases):
            return {"success": False, "error": "阶段索引无效"}

        target_phase = phases[phase_index]

        user_msg = DAILY_TASK_USER.format(
            user_profile=json.dumps(user_profile, cls=DecimalEncoder, ensure_ascii=False, indent=2),
            target_job=target_job.get("job_title", ""),
            phase=json.dumps(target_phase, cls=DecimalEncoder, ensure_ascii=False, indent=2),
            start_date=datetime.now().strftime("%Y-%m-%d")
        )

        response = self.llm.invoke([
            ("system", DAILY_TASK_SYSTEM),
            ("human", user_msg)
        ])

        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        try:
            # 尝试直接解析
            result = json.loads(content.strip())
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"原始内容: {content[:500]}")
            # 尝试修复常见的JSON格式问题
            try:
                # 移除可能的多余空格和换行
                content = content.replace('\n', ' ').replace('  ', ' ')
                # 确保所有字符串使用双引号
                result = json.loads(content.strip())
            except json.JSONDecodeError as e2:
                print(f"修复后仍然解析错误: {e2}")
                # 返回一个默认的任务列表
                tasks = [
                    DailyTask(
                        user_id=user_id,
                        phase_index=phase_index,
                        title="学习计划准备",
                        description="整理学习资料，制定详细的学习计划",
                        duration="1天",
                        resources=["学习指南", "参考书籍"],
                        status="pending"
                    )
                ]
                save_daily_tasks(tasks)
                return {
                    "success": True,
                    "tasks": [t.to_dict() for t in tasks],
                    "warning": "JSON解析失败，使用默认任务"
                }

        tasks = []
        for item in result.get("tasks", []):
            task = DailyTask(
                user_id=user_id,
                phase_index=phase_index,
                title=item.get("title", ""),
                description=item.get("description", ""),
                duration=item.get("duration", "1天"),
                resources=item.get("resources", []),
                status="pending"
            )
            tasks.append(task)

        if not tasks:
            # 如果没有生成任务，添加默认任务
            tasks = [
                DailyTask(
                    user_id=user_id,
                    phase_index=phase_index,
                    title="学习计划准备",
                    description="整理学习资料，制定详细的学习计划",
                    duration="1天",
                    resources=["学习指南", "参考书籍"],
                    status="pending"
                )
            ]

        save_daily_tasks(tasks)

        return {
            "success": True,
            "tasks": [t.to_dict() for t in tasks]
        }

    def adjust_tasks(self, user_id: int, completed_task_ids: List[int], remaining_tasks: List[Dict]) -> Dict[str, Any]:
        user_msg = TASK_ADJUST_USER.format(
            remaining_tasks=json.dumps(remaining_tasks, cls=DecimalEncoder, ensure_ascii=False, indent=2),
            completed_count=len(completed_task_ids)
        )

        response = self.llm.invoke([
            ("system", TASK_ADJUST_SYSTEM),
            ("human", user_msg)
        ])

        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        try:
            result = json.loads(content.strip())
        except json.JSONDecodeError:
            return {"success": False, "error": f"JSON解析失败: {content[:200]}"}

        new_tasks = []
        for item in result.get("adjusted_tasks", []):
            task = DailyTask(
                user_id=user_id,
                phase_index=remaining_tasks[0].get("phase_index", 0) if remaining_tasks else 0,
                title=item.get("title", ""),
                description=item.get("description", ""),
                duration=item.get("duration", "1天"),
                resources=item.get("resources", []),
                status="pending"
            )
            new_tasks.append(task)

        if new_tasks:
            save_daily_tasks(new_tasks)

        return {
            "success": True,
            "adjusted_tasks": [t.to_dict() for t in new_tasks],
            "adjustment_reason": result.get("reason", "")
        }

    def export_plan(self, user_id: int) -> Dict[str, Any]:
        plan_data = get_learning_plan(user_id)
        if not plan_data:
            return {"success": False, "error": "未找到学习计划"}

        export_text = f"""# 学习计划报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 目标岗位
{plan_data.get('target_job', '')}

## 计划类型
{plan_data.get('plan_type', '')}长期

## 学习阶段

"""

        for i, phase in enumerate(plan_data.get("phases", [])):
            export_text += f"""### 第{i+1}阶段: {phase.get('阶段名称', f'阶段{i+1}')}
**时间范围**: {phase.get('时间范围', '未知')}
**核心目标**: {phase.get('核心目标', '未知')}

**学习内容**:
"""
            for content in phase.get("学习内容", []):
                export_text += f"- {content}\n"

            export_text += f"""
**推荐资源**:
"""
            for resource in phase.get("推荐资源", []):
                export_text += f"- {resource}\n"

            export_text += "\n"

        return {
            "success": True,
            "export_text": export_text,
            "filename": f"learning_plan_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        }


agent = LearningPlanAgent()


def run_learning_plan(user_id: int, action: str, **kwargs) -> Dict[str, Any]:
    if action == "generate":
        return agent.generate_plan(user_id, kwargs.get("plan_type", "长期"))
    elif action == "polish":
        return agent.polish_plan(kwargs.get("current_plan", {}), kwargs.get("user_feedback", ""))
    elif action == "daily_tasks":
        return agent.generate_daily_tasks(user_id, kwargs.get("phase_index", 0))
    elif action == "adjust":
        return agent.adjust_tasks(
            user_id,
            kwargs.get("completed_task_ids", []),
            kwargs.get("remaining_tasks", [])
        )
    elif action == "export":
        return agent.export_plan(user_id)
    else:
        return {"success": False, "error": f"未知动作: {action}"}