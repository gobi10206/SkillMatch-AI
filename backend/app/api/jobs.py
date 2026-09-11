"""
Job and internship browsing/matching, plus employer job creation.
`/jobs` and `/internships` share one table (Job.job_type) filtered
differently, per the Phase 20 requirement for a dedicated internship
filter set.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.users import User
from app.models.profiles import Profile
from app.models.jobs import Company, Job, JobSkill
from app.matching.job_matching import match_jobs_for_profile
from app.schemas.jobs import JobCreate, JobOut, JobMatchOut

router = APIRouter()


def _own_profile(db: Session, user: User) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    location: str | None = None, is_remote: bool | None = None,
    experience_level: str | None = None, db: Session = Depends(get_db),
):
    query = db.query(Job).filter(Job.is_active == True, Job.job_type == "full_time")  # noqa: E712
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if is_remote is not None:
        query = query.filter(Job.is_remote == is_remote)
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)
    return query.all()


@router.get("/internships", response_model=list[JobOut])
def list_internships(
    location: str | None = None, is_remote: bool | None = None,
    experience_level: str | None = None, db: Session = Depends(get_db),
):
    query = db.query(Job).filter(Job.is_active == True, Job.job_type == "internship")  # noqa: E712
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if is_remote is not None:
        query = query.filter(Job.is_remote == is_remote)
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)
    return query.all()


@router.post("/jobs/match", response_model=list[JobMatchOut])
def match_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = _own_profile(db, user)
    results = match_jobs_for_profile(profile.id, db)
    return [
        JobMatchOut(
            job_id=r.job_id, job_title=r.job_title, match_score=r.match_score,
            matched_skills=r.matched_skills, missing_skills=r.missing_skills, explanation=r.explanation,
        )
        for r in results
    ]


@router.post("/jobs", response_model=JobOut, status_code=201)
def create_job(
    payload: JobCreate, db: Session = Depends(get_db),
    user: User = Depends(require_role("employer")),
):
    company = db.query(Company).filter(Company.owner_user_id == user.id).first()
    if not company:
        raise HTTPException(status_code=400, detail="Create a company profile before posting jobs")

    job = Job(
        company_id=company.id, title=payload.title, description=payload.description,
        job_type=payload.job_type, location=payload.location, is_remote=payload.is_remote,
        experience_level=payload.experience_level, stipend_or_salary_note=payload.stipend_or_salary_note,
    )
    db.add(job)
    db.flush()

    for rs in payload.required_skills:
        db.add(JobSkill(job_id=job.id, skill_id=rs.skill_id, is_required=rs.is_required))

    db.commit()
    db.refresh(job)
    return job
