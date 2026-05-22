from fastapi import APIRouter, Depends
from app.agents.registry import get_agent
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/match")
async def match_jobs(user: dict = Depends(get_current_user)):
    agent = get_agent("job_matcher")
    result = await agent.run({"user_id": user["user_id"]})
    return {"success": True, "data": result}
