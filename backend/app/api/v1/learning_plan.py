from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.agents.registry import get_agent
from app.agents.learning_plan import tools
from app.middleware.auth import get_current_user

router = APIRouter()


class GenerateRequest(BaseModel):
    plan_type: str = "长期"


class PolishRequest(BaseModel):
    feedback: str


class DailyTasksRequest(BaseModel):
    phase_index: int = 0
    phase_data: Optional[dict] = None
    start_date: Optional[str] = None


class AdjustRequest(BaseModel):
    completed_tasks: List[int] = []
    remaining_tasks: List[dict] = []


class TaskUpdateRequest(BaseModel):
    status: str


@router.post("/generate")
async def generate_plan(req: GenerateRequest, user: dict = Depends(get_current_user)):
    agent = get_agent("learning_plan")
    result = await agent.run({
        "user_id": user["user_id"], "action": "generate", "plan_type": req.plan_type,
    })
    return {"success": True, "data": result}


@router.post("/polish")
async def polish_plan(req: PolishRequest, user: dict = Depends(get_current_user)):
    agent = get_agent("learning_plan")
    result = await agent.run({
        "user_id": user["user_id"], "action": "polish", "user_feedback": req.feedback,
    })
    return {"success": True, "data": result}


@router.post("/daily-tasks")
async def generate_daily_tasks(req: DailyTasksRequest, user: dict = Depends(get_current_user)):
    agent = get_agent("learning_plan")
    result = await agent.run({
        "user_id": user["user_id"], "action": "daily_tasks", "phase_index": req.phase_index,
    })
    return {"success": True, "data": result}


@router.post("/adjust")
async def adjust_tasks(req: AdjustRequest, user: dict = Depends(get_current_user)):
    agent = get_agent("learning_plan")
    result = await agent.run({
        "user_id": user["user_id"],
        "action": "adjust",
        "completed_task_ids": req.completed_tasks,
        "remaining_tasks": req.remaining_tasks,
    })
    return {"success": True, "data": result}


@router.post("/export")
async def export_plan(user: dict = Depends(get_current_user)):
    agent = get_agent("learning_plan")
    result = await agent.run({
        "user_id": user["user_id"], "action": "export",
    })
    return {"success": True, "data": result}


@router.get("/tasks")
async def get_tasks(user: dict = Depends(get_current_user)):
    tasks = await tools.get_daily_tasks(user["user_id"])
    return {"success": True, "data": tasks}


@router.put("/tasks/{task_id}")
async def update_task(task_id: int, req: TaskUpdateRequest, user: dict = Depends(get_current_user)):
    await tools.update_task_status(task_id, req.status)
    return {"success": True}


@router.post("/tasks/{task_id}/complete")
async def complete_task(task_id: int, user: dict = Depends(get_current_user)):
    await tools.update_task_status(task_id, "completed")
    return {"success": True}
