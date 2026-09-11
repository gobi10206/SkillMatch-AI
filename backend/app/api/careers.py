"""
Career browsing, recommendation, skill-gap, and readiness-score
endpoints. All operate on the current user's own profile.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.models.profiles import Profile
from app.models.careers import Career
from app.services.career_recommendation import recommend_careers, calculate_skill_gap
from app.services.career_readiness import calculate_readiness
from app.schemas.careers import CareerOut, SkillGapOut, ReadinessOut

router = APIRouter()


def _own_profile(db: Session, user: User) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("", response_model=list[CareerOut])
def list_careers(db: Session = Depends(get_db)):
    return db.query(Career).all()


@router.get("/recommend", response_model=list[SkillGapOut])
def recommend(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _own_profile(db, user)
    results = recommend_careers(profile.id, db)
    return [
        SkillGapOut(
            career_id=r.career_id, career_title=r.career_title, match_score=r.match_score,
            existing_skills=r.existing_skills, missing_skills=r.missing_skills, explanation=r.explanation,
        )
        for r in results
    ]


@router.get("/{career_id}/skill-gap", response_model=SkillGapOut)
def skill_gap(career_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _own_profile(db, user)
    career = db.get(Career, career_id)
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    r = calculate_skill_gap(profile.id, career, db)
    return SkillGapOut(
        career_id=r.career_id, career_title=r.career_title, match_score=r.match_score,
        existing_skills=r.existing_skills, missing_skills=r.missing_skills, explanation=r.explanation,
    )


@router.get("/{career_id}/readiness", response_model=ReadinessOut)
def readiness(career_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _own_profile(db, user)
    career = db.get(Career, career_id)
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    r = calculate_readiness(profile, career, db)
    return ReadinessOut(**r.__dict__)
