"""
Skill taxonomy (Skills), the join between profiles and skills
(UserSkill), and SkillEvidence — the source text/evidence behind an
AI-inferred skill, which is what lets a user see *why* a skill was
suggested and decide whether to verify it.
"""
import uuid

from app.core.vector_type import PortableVector as Vector
from sqlalchemy import ForeignKey, String, Text, Float, Boolean
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin

EMBEDDING_DIM = 384  # matches all-MiniLM-L6-v2 output size


class Skill(Base, TimestampMixin):
    """
    Standardized skill taxonomy node, e.g. "Computer Troubleshooting"
    under category "IT Support". Synonyms let normalization map raw
    phrases ("debugging computers") onto this canonical skill.
    """
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. Programming, Soft Skills
    parent_category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. Technology
    skill_type: Mapped[str] = mapped_column(String(20), nullable=False, default="technical")  # technical | soft
    synonyms: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma-separated
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)


class UserSkill(Base, TimestampMixin):
    """
    A skill attached to a profile. `source` distinguishes AI-inferred
    from user-verified per the AI-safety requirement that inference
    is never silently presented as fact.
    """
    __tablename__ = "user_skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("skills.id"), nullable=False)
    proficiency_level: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="ai_inferred")  # ai_inferred | user_verified
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # AI extraction confidence, 0-1
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    profile = relationship("Profile", back_populates="user_skills")
    skill = relationship("Skill")
    evidence = relationship("SkillEvidence", back_populates="user_skill", cascade="all, delete-orphan")


class SkillEvidence(Base, TimestampMixin):
    """
    The source snippet (resume line, informal-experience text) that
    led the AI to infer a given UserSkill — shown to the user so the
    inference is explainable and correctable.
    """
    __tablename__ = "skill_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_skill_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("user_skills.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)  # resume | informal_experience | manual
    source_text: Mapped[str] = mapped_column(Text, nullable=False)

    user_skill = relationship("UserSkill", back_populates="evidence")
