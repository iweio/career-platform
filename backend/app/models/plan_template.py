from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.mysql import JSON
from app.models.base import Base


class PlanTemplate(Base):
    __tablename__ = "plan_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    target_job = Column(String(100))
    plan_type = Column(String(50), default="长期")
    phases = Column(JSON)
    created_at = Column(DateTime, default=func.now())
