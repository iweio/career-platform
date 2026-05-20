from typing import List, Optional, Any
from pydantic import BaseModel, Field


class TrendPrediction(BaseModel):
    job_name: str = Field(description="岗位名称")
    years: List[int] = Field(description="年份列表 [2026,2027,2028,2029,2030]")
    salary: List[int] = Field(description="薪资列表 (CNY/月)")
    salary_unit: str = Field(default="CNY/月", description="薪资单位")
    demand: List[int] = Field(description="需求指数列表 (0-100)")
    demand_unit: str = Field(default="指数(0-100)", description="需求单位")


class CareerPhase(BaseModel):
    阶段: str = Field(description="阶段名称，如 '第一阶段(2026-2027)'")
    目标: str = Field(description="阶段目标")
    能力要求: List[str] = Field(description="需要提升的能力")
    薪资预期: str = Field(description="该阶段薪资预期")
    时间节点: str = Field(description="预计达成时间")


class CareerPath(BaseModel):
    current: str = Field(description="当前岗位")
    target: str = Field(description="最终目标")
    phases: List[CareerPhase] = Field(description="分阶段路径列表")


class CareerPlanResult(BaseModel):
    success: bool = Field(description="是否成功")
    error: Optional[str] = Field(default=None, description="错误信息")
    top_job: Optional[str] = Field(default=None, description="匹配度最高的岗位")
    match_score: Optional[float] = Field(default=None, description="匹配分数")
    trends: Optional[TrendPrediction] = Field(default=None, description="趋势预测")
    career_path: Optional[CareerPath] = Field(default=None, description="职业路径")
    chart_path: Optional[str] = Field(default=None, description="图表保存路径")
