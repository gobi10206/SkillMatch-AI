"""
Admin-only endpoints. User/job/course management here are the
minimal CRUD needed for a working demo; the fairness dashboard route
is the one called out explicitly in the spec (GET /admin/fairness).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_role
from app.models.users import User
from app.models.jobs import Job
from app.models.fairness import FairnessMetric
from app.fairness.metrics import compute_selection_rate_parity

router = APIRouter()


@router.get("/users")
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_role("admin"))):
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active} for u in users]


@router.put("/users/{user_id}/deactivate")
def deactivate_user(user_id: str, db: Session = Depends(get_db), admin: User = Depends(require_role("admin"))):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"id": user.id, "is_active": user.is_active}


@router.put("/jobs/{job_id}/flag")
def flag_job(job_id: str, db: Session = Depends(get_db), admin: User = Depends(require_role("admin"))):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.is_active = False
    db.commit()
    return {"id": job.id, "is_active": job.is_active}


@router.get("/fairness")
def fairness_dashboard(period: str = "current", db: Session = Depends(get_db), admin: User = Depends(require_role("admin"))):
    """
    Recomputes and returns current fairness metrics. Response
    explicitly documents scope/limitations per Phase 22 — this is
    NOT a bias-free certification, and small groups are excluded.
    """
    live = compute_selection_rate_parity(db, period)
    stored = db.query(FairnessMetric).filter(FairnessMetric.computed_for_period == period).all()

    return {
        "metrics": [{"name": m.metric_name, "group": m.group_label, "value": m.value, "sample_size": m.sample_size} for m in stored]
                   or [{"name": "selection_rate_parity", "group": r.group_label, "value": r.selection_rate, "sample_size": r.sample_size} for r in live],
        "data_used": ["voluntary, consented demographic survey responses", "computed match scores"],
        "data_not_used": ["race", "religion", "gender", "caste", "disability", "political affiliation — none of these ever enter the ranking pipeline"],
        "limitations": "Aggregated statistics only; groups below the minimum sample size are suppressed. This dashboard reports fairness-aware, bias-mitigated metrics — it does not certify the system as bias-free.",
    }
