"""
Profile endpoints. All routes operate on the current user's own
profile — there is no "get any profile by id" route here to avoid
accidentally exposing another job seeker's data (employers view
candidates only through the matching/search flow, added in Phase 15).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.models.profiles import Profile, Experience, Education, Project
from app.schemas.profiles import (
    ProfileOut, ProfileUpdate, ExperienceIn, ExperienceOut, EducationIn, EducationOut, ProjectIn, ProjectOut,
)
from app.services.profile_completion import calculate_completion

router = APIRouter()


def _get_own_profile(db: Session, user: User) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found for this account")
    return profile


@router.get("", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_own_profile(db, user)


@router.put("", response_model=ProfileOut)
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _get_own_profile(db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    profile.profile_completion_pct = calculate_completion(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/experiences", response_model=ExperienceOut, status_code=201)
def add_experience(payload: ExperienceIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _get_own_profile(db, user)
    exp = Experience(profile_id=profile.id, **payload.model_dump())
    db.add(exp)
    profile.profile_completion_pct = calculate_completion(profile)
    db.commit()
    db.refresh(exp)
    return exp


@router.post("/education", response_model=EducationOut, status_code=201)
def add_education(payload: EducationIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _get_own_profile(db, user)
    edu = Education(profile_id=profile.id, **payload.model_dump())
    db.add(edu)
    profile.profile_completion_pct = calculate_completion(profile)
    db.commit()
    db.refresh(edu)
    return edu


@router.post("/projects", response_model=ProjectOut, status_code=201)
def add_project(payload: ProjectIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _get_own_profile(db, user)
    proj = Project(profile_id=profile.id, **payload.model_dump())
    db.add(proj)
    profile.profile_completion_pct = calculate_completion(profile)
    db.commit()
    db.refresh(proj)
    return proj
