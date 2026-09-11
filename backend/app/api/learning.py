"""
Learning path endpoints: generate/regenerate a path for a target
career, view it with progress, and update per-module progress
(Phase 16 micro-learning tracking).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.models.profiles import Profile
from app.models.careers import Career
from app.models.learning import LearningPath, LearningModule, LearningProgress
from app.services.learning_engine import generate_learning_path
from app.schemas.careers import LearningPathOut, LearningModuleOut, ProgressUpdateIn

router = APIRouter()


def _own_profile(db: Session, user: User) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def _serialize(path: LearningPath, db: Session) -> LearningPathOut:
    modules_out = []
    for m in path.modules:
        progress = db.query(LearningProgress).filter(
            LearningProgress.module_id == m.id, LearningProgress.profile_id == path.profile_id
        ).first()
        modules_out.append(LearningModuleOut(
            id=m.id, sequence=m.sequence, skill_name=m.skill.name,
            learning_objective=m.learning_objective, estimated_effort_hours=m.estimated_effort_hours,
            recommended_course_title=m.recommended_course.title if m.recommended_course else None,
            status=progress.status if progress else "not_started",
            completion_pct=progress.completion_pct if progress else 0,
        ))
    return LearningPathOut(
        id=path.id, career_title=path.career.title,
        estimated_weeks_min=path.estimated_weeks_min, estimated_weeks_max=path.estimated_weeks_max,
        modules=modules_out,
    )


@router.post("/path/{career_id}", response_model=LearningPathOut)
def create_or_regenerate_path(career_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _own_profile(db, user)
    career = db.get(Career, career_id)
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    path = generate_learning_path(profile.id, career, db)
    return _serialize(path, db)


@router.get("/path/{career_id}", response_model=LearningPathOut)
def get_path(career_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _own_profile(db, user)
    path = db.query(LearningPath).filter(
        LearningPath.profile_id == profile.id, LearningPath.career_id == career_id
    ).first()
    if not path:
        raise HTTPException(status_code=404, detail="No learning path yet — create one first")
    return _serialize(path, db)


@router.get("/progress", response_model=list[LearningPathOut])
def all_progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _own_profile(db, user)
    paths = db.query(LearningPath).filter(LearningPath.profile_id == profile.id).all()
    return [_serialize(p, db) for p in paths]


@router.put("/modules/{module_id}/progress", response_model=LearningModuleOut)
def update_module_progress(
    module_id: str, payload: ProgressUpdateIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    profile = _own_profile(db, user)
    module = db.get(LearningModule, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    progress = db.query(LearningProgress).filter(
        LearningProgress.module_id == module_id, LearningProgress.profile_id == profile.id
    ).first()
    if not progress:
        progress = LearningProgress(module_id=module_id, profile_id=profile.id)
        db.add(progress)

    progress.status = payload.status
    progress.completion_pct = payload.completion_pct
    db.commit()

    return LearningModuleOut(
        id=module.id, sequence=module.sequence, skill_name=module.skill.name,
        learning_objective=module.learning_objective, estimated_effort_hours=module.estimated_effort_hours,
        recommended_course_title=module.recommended_course.title if module.recommended_course else None,
        status=progress.status, completion_pct=progress.completion_pct,
    )
