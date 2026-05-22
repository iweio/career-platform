"""Database tools for learning_plan agent — SQLAlchemy ORM."""

from datetime import date
from sqlalchemy import select, func, update
from sqlalchemy.dialects.mysql import insert as mysql_insert
from app.db.mysql import AsyncSessionLocal
from app.models.matching import MatchingReport
from app.models.learning import LearningPlan, DailyTask


async def get_target_job(user_id: int) -> dict | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MatchingReport.job_name, MatchingReport.match_score)
            .where(MatchingReport.user_id == user_id)
            .order_by(MatchingReport.match_score.desc()).limit(1)
        )
        row = result.first()
        return {"job_name": row[0], "match_score": float(row[1])} if row else None


async def save_learning_plan(user_id: int, target_job: str,
                               plan_type: str, phases: list) -> bool:
    async with AsyncSessionLocal() as db:
        stmt = mysql_insert(LearningPlan).values(
            user_id=user_id, target_job=target_job, plan_type=plan_type, phases=phases,
        ).on_duplicate_key_update(
            target_job=target_job, plan_type=plan_type,
            phases=phases, updated_at=func.now(),
        )
        await db.execute(stmt)
        await db.commit()
    return True


async def get_learning_plan(user_id: int) -> dict | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(LearningPlan).where(LearningPlan.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return {
            "id": row.id, "user_id": row.user_id, "target_job": row.target_job,
            "plan_type": row.plan_type, "phases": row.phases,
        }


async def save_daily_tasks(user_id: int, tasks: list[dict]) -> int:
    from sqlalchemy import delete as sql_delete
    count = 0
    async with AsyncSessionLocal() as db:
        # Clear old tasks for today before inserting
        await db.execute(
            sql_delete(DailyTask).where(
                DailyTask.user_id == user_id,
                DailyTask.task_date == date.today(),
            )
        )
        for task in tasks:
            db.add(DailyTask(
                user_id=user_id,
                task_date=date.today(),
                title=task.get("title", ""),
                description=task.get("description", ""),
                duration=task.get("duration", ""),
                resources=task.get("resources", []),
            ))
            count += 1
        await db.commit()
    return count


async def get_daily_tasks(user_id: int) -> list[dict]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(DailyTask).where(DailyTask.user_id == user_id)
            .order_by(DailyTask.task_date, DailyTask.id)
        )
        return [
            {
                "id": t.id, "task_date": str(t.task_date) if t.task_date else None,
                "title": t.title, "description": t.description,
                "duration": t.duration, "status": t.status,
            }
            for t in result.scalars().all()
        ]


async def update_task_status(task_id: int, status: str) -> bool:
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(DailyTask).where(DailyTask.id == task_id).values(status=status)
        )
        await db.commit()
    return True
