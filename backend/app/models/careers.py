"""
Careers (e.g. "Backend Developer") and the skills required for each,
with a required/optional flag and a minimum proficiency level used
by the skill-gap analyzer (Phase 10).
"""
import uuid

from app.core.vector_type import PortableVector as Vector
from sqlalchemy import ForeignKey, String, Text, Boolean
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin
from app.models.skills import EMBEDDING_DIM


class Career(Base, TimestampMixin):
    __tablename__ = "careers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    career_skills = relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")


class CareerSkill(Base, TimestampMixin):
    __tablename__ = "career_skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    career_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("careers.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_proficiency_level: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")

    career = relationship("Career", back_populates="career_skills")
    skill = relationship("Skill")
