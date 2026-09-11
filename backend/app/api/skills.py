"""
Skill taxonomy browsing plus the informal-experience extraction
endpoint (Phase 12) and the accept/reject/edit review flow (Phase 38
feedback loop) that turns an ai_inferred UserSkill into a
user_verified one, or discards/adjusts it.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.models.profiles import Profile
from app.models.skills import Skill, UserSkill, SkillEvidence
from app.ai.skill_extraction import extract_skills
from app.schemas.skills import (
    InformalExperienceIn, ResumeAnalyzeOut, ExtractedSkillOut, SkillReviewAction, UserSkillOut,
)

router = APIRouter()


@router.get("")
def list_skills(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    return [{"id": s.id, "name": s.name, "category": s.category, "skill_type": s.skill_type} for s in query.all()]


@router.post("/extract-informal", response_model=ResumeAnalyzeOut)
def extract_from_informal_experience(
    payload: InformalExperienceIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    The 'I repaired computers for my village...' flow — same
    extraction pipeline as resumes, applied to free-text informal
    experience so unconventional work is captured too.
    """
    extracted = extract_skills(payload.description, db)
    return ResumeAnalyzeOut(
        extracted_text_preview=payload.description[:500],
        extracted_skills=[ExtractedSkillOut(**e.__dict__) for e in extracted],
    )


@router.post("/verify", response_model=list[UserSkillOut])
def verify_skills(
    actions: list[SkillReviewAction], db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Apply the user's accept/reject/edit decisions from a resume or
    informal-experience review screen. 'reject' simply skips creating
    a UserSkill row; 'accept'/'edit' create one marked user_verified.
    """
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    results = []
    for action in actions:
        if action.action == "reject":
            continue
        skill = db.get(Skill, action.skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail=f"Unknown skill_id {action.skill_id}")

        existing = db.query(UserSkill).filter(
            UserSkill.profile_id == profile.id, UserSkill.skill_id == skill.id
        ).first()
        proficiency = action.proficiency_level or "beginner"

        if existing:
            existing.is_verified = True
            existing.source = "user_verified"
            if action.proficiency_level:
                existing.proficiency_level = proficiency
            user_skill = existing
        else:
            user_skill = UserSkill(
                profile_id=profile.id, skill_id=skill.id, proficiency_level=proficiency,
                source="user_verified", is_verified=True,
            )
            db.add(user_skill)

        results.append(user_skill)

    db.commit()
    for us in results:
        db.refresh(us)

    return [
        UserSkillOut(
            id=us.id, skill_id=us.skill_id, skill_name=us.skill.name,
            proficiency_level=us.proficiency_level, source=us.source,
            confidence_score=us.confidence_score, is_verified=us.is_verified,
        )
        for us in results
    ]


@router.get("/mine", response_model=list[UserSkillOut])
def my_skills(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return [
        UserSkillOut(
            id=us.id, skill_id=us.skill_id, skill_name=us.skill.name,
            proficiency_level=us.proficiency_level, source=us.source,
            confidence_score=us.confidence_score, is_verified=us.is_verified,
        )
        for us in profile.user_skills
    ]
