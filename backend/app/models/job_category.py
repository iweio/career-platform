from sqlalchemy import Column, Integer, String, DateTime, func
from app.models.base import Base


class JobCategory(Base):
    __tablename__ = "job_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(50))
    tag = Column(String(30))
    sort_order = Column(Integer, default=0)
    insight_scarcity = Column(String(30))
    created_at = Column(DateTime, default=func.now())
