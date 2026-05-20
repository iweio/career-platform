from datetime import date, datetime
from sqlalchemy import (
    String, Integer, ForeignKey, JSON, Date, DateTime, Boolean, func, Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class LearningPlan(Base):
    __tablename__ = "learning_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False
    )
    target_job: Mapped[str | None] = mapped_column(String(255))
    plan_type: Mapped[str] = mapped_column(String(50), default="长期")
    phases: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class DailyTask(Base):
    __tablename__ = "daily_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    phase_index: Mapped[int] = mapped_column(Integer, default=0)
    task_date: Mapped[date | None] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024))
    duration: Mapped[str | None] = mapped_column(String(50))
    resources: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_user_status", "user_id", "status"),
    )
