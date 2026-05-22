from datetime import date, datetime
from sqlalchemy import String, Integer, Text, Date, DateTime, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    salary_range: Mapped[str | None] = mapped_column(String(100))
    job_description: Mapped[str | None] = mapped_column(Text)
    requirements: Mapped[str | None] = mapped_column(Text)
    publish_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_jobs_title", "job_title"),
        Index("idx_jobs_industry", "industry"),
    )
