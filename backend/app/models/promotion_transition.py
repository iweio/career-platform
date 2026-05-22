from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from app.db.mysql import Base


class PromotionTransition(Base):
    __tablename__ = "promotion_transition"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    current_role = Column(String(255), nullable=False)
    next_role = Column(String(255), nullable=False)
    required_skills = Column(JSON)
    years_exp = Column(Integer)
    transition_type = Column(String(50), default="promotion")
    created_at = Column(DateTime, default=func.now())
