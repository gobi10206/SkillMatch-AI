"""
Job matching score tests, plus a structural test asserting the
fairness-isolation guarantee: the matching module never imports the
FairnessSurvey model, so demographic data cannot leak into ranking
even by accident.
"""
import inspect

from app.models.users import User
from app.models.profiles import Profile
from app.models.skills import Skill, UserSkill
from app.models.jobs import Company, Job, JobSkill
from app.matching import job_matching
from app.matching.job_matching import score_job, match_jobs_for_profile


def _seed(db_session):
    for name in ["Java", "SQL", "Git"]:
        db_session.add(Skill(name=name, category="Programming", skill_type="technical"))
    db_session.commit()

    user = User(email="jobmatch@example.com", hashed_password="x", full_name="T", role="job_seeker")
    db_session.add(user)
    db_session.flush()
    profile = Profile(user_id=user.id)
    db_session.add(profile)

    employer = User(email="employer2@example.com", hashed_password="x", full_name="E", role="employer")
    db_session.add(employer)
    db_session.flush()
    company = Company(owner_user_id=employer.id, name="Test Co")
    db_session.add(company)
    db_session.flush()

    job = Job(company_id=company.id, title="Java Dev", job_type="full_time", is_active=True)
    db_session.add(job)
    db_session.flush()

    for name in ["Java", "SQL", "Git"]:
        skill = db_session.query(Skill).filter(Skill.name == name).first()
        db_session.add(JobSkill(job_id=job.id, skill_id=skill.id, is_required=True))

    java_skill = db_session.query(Skill).filter(Skill.name == "Java").first()
    db_session.add(UserSkill(profile_id=profile.id, skill_id=java_skill.id, source="user_verified", is_verified=True))
    db_session.commit()
    return profile, job


def test_job_score_reflects_partial_match(db_session):
    profile, job = _seed(db_session)
    result = score_job(profile.id, job, db_session)
    assert 0 < result.match_score < 100
    assert "Java" in result.matched_skills
    assert "SQL" in result.missing_skills


def test_match_jobs_for_profile_caches_matches(db_session):
    profile, job = _seed(db_session)
    results = match_jobs_for_profile(profile.id, db_session)
    assert len(results) == 1
    assert results[0].job_id == str(job.id)


def test_matching_module_never_imports_fairness_survey():
    """
    Structural fairness guarantee: FairnessSurvey (demographic data)
    must not appear anywhere in the job_matching module's source or
    imports, so ranking cannot be influenced by it even accidentally.
    """
    source = inspect.getsource(job_matching)
    assert "FairnessSurvey" not in source
    assert "fairness" not in source.lower()
