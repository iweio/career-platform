"""Database utilities for job_matcher agent — SQLAlchemy ORM."""

from sqlalchemy import select, func
from sqlalchemy.dialects.mysql import insert as mysql_insert
from app.db.mysql import AsyncSessionLocal
from app.models.favorite import Favorite
from app.models.profile import UserProfile
from app.models.job import Job
from app.models.matching import MatchingReport
from app.models.career_plan import CareerPlan


async def get_user_profile(user_id: int) -> dict | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserProfile.profile_data).where(
                UserProfile.user_id == user_id, UserProfile.status == "active"
            )
        )
        row = result.first()
        return {"profile_data": row[0]} if row else None


async def get_user_favorites(user_id: int) -> list[int]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Favorite.job_id).where(Favorite.user_id == user_id)
        )
        return [r[0] for r in result.fetchall()]


async def get_job_details(job_ids: list[int]) -> list[dict]:
    if not job_ids:
        return []
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Job).where(Job.id.in_(job_ids))
        )
        jobs = result.scalars().all()
        return [
            {
                "id": j.id, "job_title": j.job_title, "company": j.company,
                "industry": j.industry, "city": j.city, "salary_range": j.salary_range,
                "job_description": j.job_description, "requirements": j.requirements,
            }
            for j in jobs
        ]


async def save_user_profile(user_id: int, profile_data: dict) -> bool:
    async with AsyncSessionLocal() as db:
        stmt = mysql_insert(UserProfile).values(
            user_id=user_id, profile_data=profile_data, status="active",
        ).on_duplicate_key_update(
            profile_data=profile_data, updated_at=func.now(),
        )
        await db.execute(stmt)
        await db.commit()
    return True


async def save_match_report(user_id: int, job_name: str, match_score: float,
                            report_data: dict, industry: str = "", city: str = "") -> int:
    async with AsyncSessionLocal() as db:
        report = MatchingReport(
            user_id=user_id, job_name=job_name, industry=industry, city=city,
            match_score=match_score, report_data=report_data,
        )
        db.add(report)
        await db.flush()
        await db.commit()
    return report.id


async def save_analysis_result(user_id: int, analysis: dict,
                                target_position: str = "", target_company: str = "") -> bool:
    async with AsyncSessionLocal() as db:
        db.add(CareerPlan(
            user_id=user_id, target_position=target_position,
            target_company=target_company, plan_data=analysis, status="active",
        ))
        await db.commit()
    return True
