from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class TrendPrediction(BaseModel):
    job_name: str = Field(description="岗位名称")
    years: List[int] = Field(description="年份列表")
    salary: List[int] = Field(description="薪资列表")
    salary_unit: str = Field(default="CNY/月")
    demand: List[int] = Field(description="需求指数列表")
    demand_unit: str = Field(default="指数")


class CareerPhase(BaseModel):
    阶段: Optional[str] = None
    目标: Optional[str] = None
    能力要求: Optional[List[str]] = None
    薪资预期: Optional[str] = None
    时间节点: Optional[str] = None

    @classmethod
    def from_llm(cls, data: Dict[str, Any]) -> "CareerPhase":
        if data is None:
            return cls()
        normalized = {}
        for key in ["阶段", "目标", "能力要求", "薪资预期", "时间节点"]:
            if key in data:
                normalized[key] = data[key]
        for eng_key, cn_key in [("stage", "阶段"), ("target", "目标"), ("requirements", "能力要求"),
                                  ("salary_expectation", "薪资预期"), ("timeline", "时间节点")]:
            if eng_key in data and cn_key not in normalized:
                normalized[cn_key] = data[eng_key]
        if "能力要求" in normalized and isinstance(normalized["能力要求"], dict):
            normalized["能力要求"] = list(normalized["能力要求"].values())
        return cls(**normalized)


class CareerPath(BaseModel):
    current: Optional[str] = None
    target: Optional[str] = None
    phases: List[CareerPhase] = Field(default_factory=list)

    @classmethod
    def from_llm(cls, data: Dict[str, Any]) -> "CareerPath":
        if data is None:
            return cls()
        phases = [CareerPhase.from_llm(p) for p in data.get("phases", [])]
        return cls(
            current=data.get("current", data.get("current_level", "")),
            target=data.get("target", data.get("target_level", "")),
            phases=phases
        )


class CareerPlanResult(BaseModel):
    success: bool = Field(default=False)
    error: Optional[str] = Field(default=None)
    top_job: Optional[str] = None
    match_score: Optional[float] = None
    trends: Optional[TrendPrediction] = None
    career_path: Optional[CareerPath] = None
    chart_path: Optional[str] = None
