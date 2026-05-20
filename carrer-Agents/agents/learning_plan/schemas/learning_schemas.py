from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class Phase(BaseModel):
    阶段名称: str = Field(default="")
    时间范围: str = Field(default="")
    核心目标: str = Field(default="")
    学习内容: List[str] = Field(default_factory=list)
    推荐资源: List[str] = Field(default_factory=list)


class LearningPlan(BaseModel):
    user_id: int
    target_job: str = ""
    plan_type: str = "长期"
    phases: List[Dict[str, Any]] = Field(default_factory=list)
    raw_response: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "target_job": self.target_job,
            "plan_type": self.plan_type,
            "phases": self.phases,
            "created_at": self.created_at
        }


class DailyTask(BaseModel):
    id: Optional[int] = None
    user_id: int
    phase_index: int = 0
    title: str = ""
    description: str = ""
    duration: str = "1天"
    resources: List[str] = Field(default_factory=list)
    status: str = "pending"
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "phase_index": self.phase_index,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "resources": self.resources,
            "status": self.status,
            "created_at": self.created_at
        }


class PlanGenerationRequest(BaseModel):
    user_id: int
    plan_type: str = "长期"