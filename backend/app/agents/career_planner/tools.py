"""Database tools for career_planner agent — SQLAlchemy ORM."""

from sqlalchemy import select
from app.db.mysql import AsyncSessionLocal
from app.models.matching import MatchingReport, PromotionTransition
from app.models.career_plan import CareerPlan


async def get_top_matched_job(user_id: int) -> dict | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MatchingReport).where(MatchingReport.user_id == user_id)
            .order_by(MatchingReport.match_score.desc()).limit(1)
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return {
            "job_name": row.job_name, "industry": row.industry,
            "city": row.city, "match_score": float(row.match_score) if row.match_score else None,
            "report_data": row.report_data,
        }


async def get_promotion_transitions(job_name: str) -> list[dict]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PromotionTransition).where(
                PromotionTransition.current_role.contains(job_name)
                | PromotionTransition.next_role.contains(job_name)
            )
        )
        rows = result.scalars().all()
        return [
            {
                "current_role": r.current_role, "next_role": r.next_role,
                "required_skills": r.required_skills, "years_exp": r.years_exp,
                "transition_type": r.transition_type,
            }
            for r in rows
        ]


async def save_career_plan(user_id: int, top_job: dict, match_score: float,
                            trends: dict, career_path: dict) -> int:
    plan_data = {
        "top_job": top_job,
        "match_score": match_score,
        "trends": trends,
        "career_path": career_path,
    }

    async with AsyncSessionLocal() as db:
        plan = CareerPlan(
            user_id=user_id,
            target_position=top_job.get("job_name", ""),
            target_company="",
            plan_data=plan_data,
            status="active",
        )
        db.add(plan)
        await db.flush()
        await db.commit()
    return plan.id
