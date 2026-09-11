"""Application tracker — saved/applied/interview/assessment/offer/rejected."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.models.profiles import Profile
from app.models.jobs import Job, Application
from app.schemas.jobs import ApplicationCreate, ApplicationUpdate, ApplicationOut

router = APIRouter()

VALID_STATUSES = {"saved", "applied", "interview", "assessment", "offer", "rejected"}


def _own_profile(db: Session, user: User) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def _to_out(app: Application) -> ApplicationOut:
    return ApplicationOut(
        id=app.id, job_id=app.job_id, job_title=app.job.title,
        status=app.status, applied_on=app.applied_on,
    )


@router.get("", response_model=list[ApplicationOut])
def list_applications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _own_profile(db, user)
    apps = db.query(Application).filter(Application.profile_id == profile.id).all()
    return [_to_out(a) for a in apps]


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _own_profile(db, user)
    job = db.get(Job, payload.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {sorted(VALID_STATUSES)}")

    app = Application(profile_id=profile.id, job_id=job.id, status=payload.status)
    db.add(app)
    db.commit()
    db.refresh(app)
    return _to_out(app)


@router.put("/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: str, payload: ApplicationUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    profile = _own_profile(db, user)
    app = db.query(Application).filter(
        Application.id == application_id, Application.profile_id == profile.id
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {sorted(VALID_STATUSES)}")

    app.status = payload.status
    if payload.applied_on:
        app.applied_on = payload.applied_on
    db.commit()
    db.refresh(app)
    return _to_out(app)
