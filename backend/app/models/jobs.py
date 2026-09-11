"""
Employer-side entities (Company, Job, JobSkill), the seeker-side
Application tracker, and Match — the computed, explainable result of
matching a profile against a job (Phase 12 job matching, Phase 13
fairness-aware ranking).
"""
import uuid
from datetime import date

from app.core.vector_type import PortableVector as Vector
from sqlalchemy import ForeignKey, String, Text, Boolean, Float, Date
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin
from app.models.skills import EMBEDDING_DIM


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    owner = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_type: Mapped[str] = mapped_column(String(20), nullable=False, default="full_time")  # full_time | internship
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stipend_or_salary_note: Mapped[str | None] = mapped_column(String(255), nullable=True)  # never fabricated
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    company = relationship("Company", back_populates="jobs")
    job_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")


class JobSkill(Base, TimestampMixin):
    __tablename__ = "job_skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    job = relationship("Job", back_populates="job_skills")
    skill = relationship("Skill")


class Application(Base, TimestampMixin):
    """Kanban-style tracker: saved -> applied -> interview -> assessment -> offer -> rejected."""
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="saved")
    applied_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    profile = relationship("Profile")
    job = relationship("Job")


class Match(Base, TimestampMixin):
    """
    Stored, explainable match result between a profile and a job.
    match_score and the skill breakdown are recomputed by the
    matching service (Phase 12); this table caches results for the
    dashboard and match-history views.
    """
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    matched_skills: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated skill names
    missing_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)

    profile = relationship("Profile")
    job = relationship("Job")
