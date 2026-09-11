"""
Learning resources (Course, Certification) and the personalized
LearningPath/LearningModule/LearningProgress models that drive the
Phase 11 learning-recommendation engine and Phase 16 micro-learning.
"""
import uuid

from app.core.vector_type import PortableVector as Vector
from sqlalchemy import ForeignKey, String, Text, Boolean, Integer
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin
from app.models.skills import EMBEDDING_DIM


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g. "External: Coursera"
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_external: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    course_skills = relationship("CourseSkill", back_populates="course", cascade="all, delete-orphan")


class CourseSkill(Base, TimestampMixin):
    __tablename__ = "course_skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("skills.id"), nullable=False)

    course = relationship("Course", back_populates="course_skills")
    skill = relationship("Skill")


class Certification(Base, TimestampMixin):
    __tablename__ = "certifications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issued_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    profile = relationship("Profile")


class LearningPath(Base, TimestampMixin):
    __tablename__ = "learning_paths"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    career_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("careers.id"), nullable=False)
    estimated_weeks_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_weeks_max: Mapped[int | None] = mapped_column(Integer, nullable=True)

    profile = relationship("Profile")
    career = relationship("Career")
    modules = relationship(
        "LearningModule", back_populates="learning_path", cascade="all, delete-orphan",
        order_by="LearningModule.sequence"
    )


class LearningModule(Base, TimestampMixin):
    __tablename__ = "learning_modules"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learning_path_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("learning_paths.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    learning_objective: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_effort_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recommended_course_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("courses.id"), nullable=True)

    learning_path = relationship("LearningPath", back_populates="modules")
    skill = relationship("Skill")
    recommended_course = relationship("Course")
    progress = relationship("LearningProgress", back_populates="module", cascade="all, delete-orphan")


class LearningProgress(Base, TimestampMixin):
    __tablename__ = "learning_progress"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("learning_modules.id"), nullable=False)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="not_started")  # not_started|in_progress|completed
    completion_pct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    module = relationship("LearningModule", back_populates="progress")
    profile = relationship("Profile")
