from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, func
from app.models.base import Base


class JobCategory(Base):
    __tablename__ = "job_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(50))
    tag = Column(String(30))
    sort_order = Column(Integer, default=0)
    insight_scarcity = Column(String(30))
    description = Column(Text, comment="岗位族描述，用于向量化")
    core_skills = Column(JSON, comment="核心技能列表")
    promotion_path = Column(JSON, comment="晋升路径，入Neo4j")
    transition_to = Column(JSON, comment="可转岗方向")
    created_at = Column(DateTime, default=func.now())
