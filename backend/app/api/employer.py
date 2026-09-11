"""
Employer-only endpoints: company profile creation and competency-based
candidate search. Candidate search intentionally accepts only a list
of skill names — there is no parameter for demographic filtering,
enforcing fairness architecture at the API contract level, not just
in the scoring code.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_role
from app.models.users import User
from app.models.jobs import Company
from app.models.skills import Skill, UserSkill
from app.models.profiles import Profile
from app.schemas.jobs import CompanyCreate

router = APIRouter()


@router.post("/company", status_code=201)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db), user: User = Depends(require_role("employer"))):
    existing = db.query(Company).filter(Company.owner_user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company profile already exists")

    company = Company(owner_user_id=user.id, name=payload.name, description=payload.description, website=payload.website)
    db.add(company)
    db.commit()
    db.refresh(company)
    return {"id": company.id, "name": company.name}


@router.get("/candidates/search")
def search_candidates(
    skill_names: list[str], db: Session = Depends(get_db), user: User = Depends(require_role("employer"))
):
    """
    Returns profiles that have verified skills matching the given
    skill names, ranked by overlap count. Only competency data is
    exposed — no PII beyond headline/location, no demographic fields.
    """
    skills = db.query(Skill).filter(Skill.name.in_(skill_names)).all()
    if not skills:
        return []
    skill_ids = [s.id for s in skills]

    candidates = (
        db.query(Profile)
        .join(UserSkill, UserSkill.profile_id == Profile.id)
        .filter(UserSkill.skill_id.in_(skill_ids), UserSkill.is_verified == True)  # noqa: E712
        .distinct()
        .all()
    )

    results = []
    for profile in candidates:
        matched = {us.skill.name for us in profile.user_skills if us.skill_id in skill_ids and us.is_verified}
        results.append({
            "profile_id": profile.id,
            "headline": profile.headline,
            "location": profile.location,
            "matched_skills": sorted(matched),
            "match_count": len(matched),
        })
    results.sort(key=lambda r: r["match_count"], reverse=True)
    return results
