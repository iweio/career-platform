import os
import json
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field

_dotenv_path = Path(__file__).parent.parent / ".env"
if _dotenv_path.exists():
    with open(_dotenv_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key, value)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from .schemas.career_schemas import TrendPrediction, CareerPath, CareerPlanResult
from .tools.db_tools import get_top_matched_job, get_promotion_transition, save_career_plan
from .prompts.career_prompts import TREND_SYSTEM_PROMPT, TREND_USER_PROMPT, PATH_SYSTEM_PROMPT, PATH_USER_PROMPT


class CareerPlanningAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
            model=os.getenv("OPENAI_MODEL", "deepseek-chat"),
            temperature=0.7
        )

    def get_top_job(self, user_id: int) -> Optional[Dict[str, Any]]:
        return get_top_matched_job(user_id)

    def predict_trends(self, job_name: str, user_profile: Dict[str, Any]) -> TrendPrediction:
        prompt = ChatPromptTemplate.from_messages([
            ("system", TREND_SYSTEM_PROMPT),
            ("human", TREND_USER_PROMPT)
        ])

        chain = prompt | self.llm | JsonOutputParser()
        result = chain.invoke({
            "job_name": job_name,
            "user_profile": json.dumps(user_profile, ensure_ascii=False, indent=2)
        })
        result["job_name"] = job_name
        return TrendPrediction(**result)

    def generate_career_path(
        self,
        job_name: str,
        user_profile: Dict[str, Any],
        promotion_data: List[Dict[str, Any]]
    ) -> CareerPath:
        prompt = ChatPromptTemplate.from_messages([
            ("system", PATH_SYSTEM_PROMPT),
            ("human", PATH_USER_PROMPT)
        ])

        chain = prompt | self.llm | JsonOutputParser()
        result = chain.invoke({
            "job_name": job_name,
            "user_profile": json.dumps(user_profile, ensure_ascii=False, indent=2),
            "promotion_data": json.dumps(promotion_data, ensure_ascii=False, indent=2)
        })

        if "current" not in result:
            result["current"] = job_name
        if "target" not in result:
            result["target"] = job_name

        for phase in result.get("phases", []):
            if isinstance(phase.get("能力要求"), dict):
                phase["能力要求"] = list(phase["能力要求"].values())

        return CareerPath(**result)

    def plot_trends(self, trend: TrendPrediction, output_path: str = "static/career_trends.png") -> str:
        years = trend.years
        salary = trend.salary
        demand = trend.demand

        fig, ax1 = plt.subplots(figsize=(10, 6))

        color = '#667eea'
        ax1.set_xlabel('年份', fontsize=12)
        ax1.set_ylabel('薪资 (CNY/月)', color=color, fontsize=12)
        ax1.plot(years, salary, color=color, marker='o', linewidth=2, label='薪资')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_xticks(years)

        ax2 = ax1.twinx()
        color2 = '#f44336'
        ax2.set_ylabel('需求指数 (0-100)', color=color2, fontsize=12)
        ax2.plot(years, demand, color=color2, marker='s', linewidth=2, linestyle='--', label='需求')
        ax2.tick_params(axis='y', labelcolor=color2)

        plt.title(f'{trend.job_name} - 薪资与需求趋势 (2026-2030)', fontsize=14, fontweight='bold')
        fig.tight_layout()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return output_path

    def run(self, user_id: int, user_profile: Optional[Dict[str, Any]] = None) -> CareerPlanResult:
        try:
            top_job = self.get_top_job(user_id)
            if not top_job:
                return CareerPlanResult(
                    success=False,
                    error="未找到匹配记录"
                )

            job_name = top_job.get("job_name", "未知岗位")
            match_score = top_job.get("match_score", 80.0)

            if not user_profile:
                user_profile = {
                    "name": "测试用户",
                    "skills": ["Python", "Java"],
                    "experience": "3年",
                    "education": "本科"
                }

            trends = self.predict_trends(job_name, user_profile)

            promotion_data = get_promotion_transition(job_name)
            career_path = self.generate_career_path(job_name, user_profile, promotion_data)

            chart_path = self.plot_trends(trends)

            save_career_plan(
                user_id=user_id,
                top_job=job_name,
                match_score=match_score,
                trends_data=trends.model_dump(),
                career_path_data=career_path.model_dump(),
                chart_path=chart_path
            )

            return CareerPlanResult(
                success=True,
                top_job=job_name,
                match_score=match_score,
                trends=trends,
                career_path=career_path,
                chart_path=chart_path
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return CareerPlanResult(
                success=False,
                error=str(e)
            )


agent_instance: Optional[CareerPlanningAgent] = None


def get_agent() -> CareerPlanningAgent:
    global agent_instance
    if agent_instance is None:
        agent_instance = CareerPlanningAgent()
    return agent_instance


def run_career_plan(user_id: int, user_profile: Optional[Dict[str, Any]] = None) -> CareerPlanResult:
    return get_agent().run(user_id, user_profile)
