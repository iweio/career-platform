from datetime import date, datetime
from sqlalchemy import String, Integer, ForeignKey, JSON, Date, DateTime, DECIMAL, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class MatchingReport(Base):
    __tablename__ = "matching_report"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    job_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    match_score: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    report_data: Mapped[dict | None] = mapped_column(JSON)
    publish_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )


class PromotionTransition(Base):
    __tablename__ = "promotion_transition"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("jobs.id"))
    current_role: Mapped[str] = mapped_column(String(255), nullable=False)
    next_role: Mapped[str] = mapped_column(String(255), nullable=False)
    required_skills: Mapped[dict | None] = mapped_column(JSON)
    years_exp: Mapped[int | None] = mapped_column(Integer)
    transition_type: Mapped[str] = mapped_column(String(50), default="promotion")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
