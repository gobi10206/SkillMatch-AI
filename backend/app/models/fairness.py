"""
Fairness architecture, enforced at the schema level:

- FairnessSurvey holds any voluntary demographic data, completely
  separate from Profile/UserSkill/Match. No FK from ranking tables
  points into it, and no FK from it points into ranking tables — the
  only link is user_id, and only the fairness-metrics service is
  expected to join across that boundary.
- FairnessMetric stores aggregated, admin-dashboard-only statistics
  (never per-user rows that could re-identify someone).
"""
import uuid

from sqlalchemy import ForeignKey, String, Float, Integer, Text
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base, TimestampMixin


class FairnessSurvey(Base, TimestampMixin):
    """Voluntary, isolated demographic data — never joined into matching/ranking queries."""
    __tablename__ = "fairness_survey"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    consent_given: Mapped[bool] = mapped_column(default=False, nullable=False)
    # Free-text/category fields intentionally generic; exact fields
    # collected are a policy decision made in a later phase together
    # with legal/compliance review, not hard-coded here.
    demographic_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # encrypted JSON blob at rest


class FairnessMetric(Base, TimestampMixin):
    """Aggregated, group-level statistics only — no individual user rows."""
    __tablename__ = "fairness_metrics"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. selection_rate_parity
    group_label: Mapped[str] = mapped_column(String(100), nullable=False)  # aggregated group, min group size enforced
    value: Mapped[float] = mapped_column(Float, nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_for_period: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. "2026-Q3"
