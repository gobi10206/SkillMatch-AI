"""
Public, aggregated analytics for the community/policy dashboard
(Phase 28). No authentication required since the data is already
anonymized/aggregated at the query level — appropriate for public
policy-facing dashboards.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.analytics import community

router = APIRouter()


@router.get("/skills/demand")
def skills_demand(db: Session = Depends(get_db)):
    return community.most_demanded_skills(db)


@router.get("/skills/gaps")
def skills_gaps(db: Session = Depends(get_db)):
    return community.top_skill_gaps(db)


@router.get("/careers/popular")
def careers_popular(db: Session = Depends(get_db)):
    return community.popular_career_pathways(db)
