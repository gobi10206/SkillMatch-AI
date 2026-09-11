"""
Career recommendation and skill-gap analysis.

Match score = (overlapping required+optional skill weight) / (total
required+optional skill weight) * 100, with required skills weighted
higher than optional ones. This is a transparent, explainable formula
by design (Phase 15/23) rather than an opaque model score.
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.careers import Career, CareerSkill
from app.models.skills import UserSkill

REQUIRED_WEIGHT = 2
OPTIONAL_WEIGHT = 1


@dataclass
class SkillGapResult:
    career_id: str
    career_title: str
    match_score: float
    existing_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    explanation: str = ""


def calculate_skill_gap(profile_id, career: Career, db: Session) -> SkillGapResult:
    user_skill_ids = {
        us.skill_id for us in db.query(UserSkill).filter(UserSkill.profile_id == profile_id).all()
    }

    career_skills = db.query(CareerSkill).filter(CareerSkill.career_id == career.id).all()

    total_weight = 0
    matched_weight = 0
    existing, missing = [], []

    for cs in career_skills:
        weight = REQUIRED_WEIGHT if cs.is_required else OPTIONAL_WEIGHT
        total_weight += weight
        if cs.skill_id in user_skill_ids:
            matched_weight += weight
            existing.append(cs.skill.name)
        else:
            missing.append(cs.skill.name)

    score = round((matched_weight / total_weight) * 100, 1) if total_weight else 0.0

    explanation = (
        f"Your profile matches {len(existing)} of {len(career_skills)} skills associated with "
        f"{career.title}"
        + (f", including required skills: {', '.join(existing[:5])}." if existing else ".")
        + (f" The largest gaps are: {', '.join(missing[:5])}." if missing else " No skill gaps found.")
    )

    return SkillGapResult(
        career_id=str(career.id), career_title=career.title, match_score=score,
        existing_skills=existing, missing_skills=missing, explanation=explanation,
    )


def recommend_careers(profile_id, db: Session, limit: int = 5) -> list[SkillGapResult]:
    careers = db.query(Career).all()
    results = [calculate_skill_gap(profile_id, career, db) for career in careers]
    results.sort(key=lambda r: r.match_score, reverse=True)
    return results[:limit]
