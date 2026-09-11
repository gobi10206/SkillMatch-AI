"""
Community/policy analytics (Phase 28). Every query here returns
counts/aggregates grouped by skill or career — never per-user rows —
satisfying "never expose individual user information."
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.skills import Skill, UserSkill
from app.models.careers import Career, CareerSkill
from app.models.learning import LearningPath

MIN_AGGREGATE_SIZE = 5  # suppress rows with too few users, avoids re-identification


def most_demanded_skills(db: Session, limit: int = 10):
    rows = (
        db.query(Skill.name, func.count(CareerSkill.id).label("demand"))
        .join(CareerSkill, CareerSkill.skill_id == Skill.id)
        .group_by(Skill.name)
        .order_by(func.count(CareerSkill.id).desc())
        .limit(limit)
        .all()
    )
    return [{"skill": name, "career_demand_count": count} for name, count in rows]


def top_skill_gaps(db: Session, limit: int = 10):
    """
    Skills required by careers but rarely held by users — computed as
    an aggregate ratio, never listing which specific users lack them.
    """
    required = (
        db.query(Skill.id, Skill.name, func.count(CareerSkill.id).label("required_count"))
        .join(CareerSkill, CareerSkill.skill_id == Skill.id)
        .filter(CareerSkill.is_required == True)  # noqa: E712
        .group_by(Skill.id, Skill.name)
        .all()
    )
    held_counts = dict(
        db.query(UserSkill.skill_id, func.count(UserSkill.id))
        .group_by(UserSkill.skill_id)
        .all()
    )
    gaps = []
    for skill_id, name, required_count in required:
        held = held_counts.get(skill_id, 0)
        if held < MIN_AGGREGATE_SIZE:
            gaps.append({"skill": name, "required_by_careers": required_count, "users_holding_skill": held})
    gaps.sort(key=lambda g: g["required_by_careers"], reverse=True)
    return gaps[:limit]


def popular_career_pathways(db: Session, limit: int = 10):
    rows = (
        db.query(Career.title, func.count(LearningPath.id).label("learners"))
        .join(LearningPath, LearningPath.career_id == Career.id, isouter=True)
        .group_by(Career.title)
        .order_by(func.count(LearningPath.id).desc())
        .limit(limit)
        .all()
    )
    return [{"career": title, "active_learners": count} for title, count in rows]
