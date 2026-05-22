from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.db.mysql import get_db
from app.middleware.auth import get_current_user
from app.models.profile import UserProfile
from app.models.matching import MatchingReport
from app.models.career_plan import CareerPlan

router = APIRouter(prefix="/profile")


@router.get("/analysis")
async def get_profile_analysis(user: dict = Depends(get_current_user), db=Depends(get_db)):
    user_id = user["user_id"]

    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    match_result = await db.execute(
        select(MatchingReport).where(MatchingReport.user_id == user_id).order_by(MatchingReport.match_score.desc()).limit(1)
    )
    match = match_result.scalar_one_or_none()

    plan_result = await db.execute(
        select(CareerPlan).where(CareerPlan.user_id == user_id).order_by(CareerPlan.updated_at.desc()).limit(1)
    )
    plan = plan_result.scalar_one_or_none()

    profile_data = profile.profile_data if profile else {}
    competitiveness_score = profile.match_score if profile else None

    radar_data = profile_data.get("dimensions", [])
    word_cloud = profile_data.get("skills", [])
    analysis_report = match.report_data if match else None

    return {
        "success": True,
        "data": {
            "competitiveness_score": float(competitiveness_score) if competitiveness_score else None,
            "radar_data": radar_data,
            "word_cloud": word_cloud,
            "analysis_report": analysis_report,
            "career_plan": plan.plan_data if plan else None,
        },
    }
