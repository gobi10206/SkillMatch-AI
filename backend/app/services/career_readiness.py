"""
Career readiness score — a transparent weighted breakdown, never a
black-box number (Phase 15 rule). Callers get both the total and the
per-component breakdown so the UI can answer "How was this score
calculated?".
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.careers import Career
from app.models.profiles import Profile
from app.models.learning import Certification, LearningProgress, LearningPath
from app.services.career_recommendation import calculate_skill_gap

COMPONENT_WEIGHTS = {
    "technical_skills": 0.40,
    "projects": 0.20,
    "certifications": 0.15,
    "experience": 0.25,
}


@dataclass
class ReadinessBreakdown:
    overall_pct: float
    technical_skills_pct: float
    projects_pct: float
    certifications_pct: float
    experience_pct: float
    explanation: str


def calculate_readiness(profile: Profile, career: Career, db: Session) -> ReadinessBreakdown:
    gap = calculate_skill_gap(profile.id, career, db)
    technical_pct = gap.match_score

    projects_pct = min(len(profile.projects) * 33, 100)  # 3+ projects = fully credited
    certifications_pct = min(
        db.query(Certification).filter(Certification.profile_id == profile.id).count() * 50, 100
    )
    experience_pct = min(len(profile.experiences) * 25, 100)

    overall = (
        technical_pct * COMPONENT_WEIGHTS["technical_skills"]
        + projects_pct * COMPONENT_WEIGHTS["projects"]
        + certifications_pct * COMPONENT_WEIGHTS["certifications"]
        + experience_pct * COMPONENT_WEIGHTS["experience"]
    )

    explanation = (
        f"Technical skills ({COMPONENT_WEIGHTS['technical_skills']*100:.0f}% weight): {technical_pct:.0f}%. "
        f"Projects ({COMPONENT_WEIGHTS['projects']*100:.0f}% weight): {projects_pct:.0f}%. "
        f"Certifications ({COMPONENT_WEIGHTS['certifications']*100:.0f}% weight): {certifications_pct:.0f}%. "
        f"Experience ({COMPONENT_WEIGHTS['experience']*100:.0f}% weight): {experience_pct:.0f}%."
    )

    return ReadinessBreakdown(
        overall_pct=round(overall, 1),
        technical_skills_pct=technical_pct,
        projects_pct=projects_pct,
        certifications_pct=certifications_pct,
        experience_pct=experience_pct,
        explanation=explanation,
    )
