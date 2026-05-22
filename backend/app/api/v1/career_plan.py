import logging
from fastapi import APIRouter, Depends
from app.agents.registry import get_agent
from app.middleware.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("")
async def run_career_plan(user: dict = Depends(get_current_user)):
    try:
        agent = get_agent("career_planner")
        result = await agent.run({"user_id": user["user_id"]})
    except Exception:
        logger.exception("career_planner agent failed")
        return {"success": False, "error": "Agent execution failed"}
    return {"success": True, "data": result}
