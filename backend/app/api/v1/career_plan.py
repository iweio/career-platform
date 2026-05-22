from fastapi import APIRouter, Depends
from app.agents.registry import get_agent
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("")
async def run_career_plan(user: dict = Depends(get_current_user)):
    agent = get_agent("career_planner")
    result = await agent.run({"user_id": user["user_id"]})
    return {"success": True, "data": result}
