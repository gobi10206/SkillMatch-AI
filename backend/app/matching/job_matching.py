"""
Job matching engine (Phase 19) with fairness-aware design (Phase 21)
built in from the start rather than bolted on: the scoring function
below takes only skill/experience data as input. It has no parameter
for demographic attributes and no code path that could read
FairnessSurvey — that table isn't even imported here.
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.jobs import Job, JobSkill, Match
from app.models.skills import UserSkill

REQUIRED_WEIGHT = 2
OPTIONAL_WEIGHT = 1


@dataclass
class JobMatchResult:
    job_id: str
    job_title: str
    match_score: float
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    explanation: str = ""


def score_job(profile_id, job: Job, db: Session) -> JobMatchResult:
    user_skill_ids = {
        us.skill_id for us in db.query(UserSkill).filter(UserSkill.profile_id == profile_id).all()
    }
    job_skills = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()

    total_weight, matched_weight = 0, 0
    matched, missing = [], []

    for js in job_skills:
        weight = REQUIRED_WEIGHT if js.is_required else OPTIONAL_WEIGHT
        total_weight += weight
        if js.skill_id in user_skill_ids:
            matched_weight += weight
            matched.append(js.skill.name)
        else:
            missing.append(js.skill.name)

    score = round((matched_weight / total_weight) * 100, 1) if total_weight else 0.0
    explanation = (
        f"Your profile matches {len(matched)} of {len(job_skills)} competencies required for {job.title}."
        + (f" Missing: {', '.join(missing[:5])}." if missing else "")
    )

    return JobMatchResult(
        job_id=str(job.id), job_title=job.title, match_score=score,
        matched_skills=matched, missing_skills=missing, explanation=explanation,
    )


def match_jobs_for_profile(profile_id, db: Session, limit: int = 20) -> list[JobMatchResult]:
    jobs = db.query(Job).filter(Job.is_active == True).all()  # noqa: E712
    results = [score_job(profile_id, job, db) for job in jobs]
    results.sort(key=lambda r: r.match_score, reverse=True)

    # Cache results for dashboard/history views.
    for r in results[:limit]:
        existing = db.query(Match).filter(Match.profile_id == profile_id, Match.job_id == r.job_id).first()
        if existing:
            existing.match_score = r.match_score
            existing.matched_skills = ",".join(r.matched_skills)
            existing.missing_skills = ",".join(r.missing_skills)
            existing.explanation = r.explanation
        else:
            db.add(Match(
                profile_id=profile_id, job_id=r.job_id, match_score=r.match_score,
                matched_skills=",".join(r.matched_skills), missing_skills=",".join(r.missing_skills),
                explanation=r.explanation,
            ))
    db.commit()

    return results[:limit]
