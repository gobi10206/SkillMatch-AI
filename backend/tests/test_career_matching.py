"""Tests for the transparent skill-gap and career-recommendation scoring."""
from app.models.profiles import Profile
from app.models.skills import Skill, UserSkill
from app.models.careers import Career, CareerSkill
from app.services.career_recommendation import calculate_skill_gap, recommend_careers


def _make_profile_with_skills(db_session, skill_names):
    from app.models.users import User
    user = User(email="skillgap@example.com", hashed_password="x", full_name="T", role="job_seeker")
    db_session.add(user)
    db_session.flush()
    profile = Profile(user_id=user.id)
    db_session.add(profile)
    db_session.flush()

    for name in skill_names:
        skill = db_session.query(Skill).filter(Skill.name == name).first()
        db_session.add(UserSkill(profile_id=profile.id, skill_id=skill.id, source="user_verified", is_verified=True))
    db_session.commit()
    return profile


def _make_career(db_session, title, required, optional=()):
    career = Career(title=title)
    db_session.add(career)
    db_session.flush()
    for name in required:
        skill = db_session.query(Skill).filter(Skill.name == name).first()
        db_session.add(CareerSkill(career_id=career.id, skill_id=skill.id, is_required=True))
    for name in optional:
        skill = db_session.query(Skill).filter(Skill.name == name).first()
        db_session.add(CareerSkill(career_id=career.id, skill_id=skill.id, is_required=False))
    db_session.commit()
    return career


def _seed_base_skills(db_session):
    for name in ["Java", "Git", "SQL", "Spring Boot", "REST APIs", "Testing"]:
        db_session.add(Skill(name=name, category="Programming", skill_type="technical"))
    db_session.commit()


def test_full_skill_match_scores_100(db_session):
    _seed_base_skills(db_session)
    career = _make_career(db_session, "Backend Developer", required=["Java", "Git", "SQL"])
    profile = _make_profile_with_skills(db_session, ["Java", "Git", "SQL"])

    result = calculate_skill_gap(profile.id, career, db_session)
    assert result.match_score == 100.0
    assert result.missing_skills == []


def test_partial_skill_match_reports_gap(db_session):
    _seed_base_skills(db_session)
    career = _make_career(db_session, "Backend Developer", required=["Java", "Git", "SQL", "Spring Boot"])
    profile = _make_profile_with_skills(db_session, ["Java", "Git"])

    result = calculate_skill_gap(profile.id, career, db_session)
    assert 0 < result.match_score < 100
    assert "SQL" in result.missing_skills
    assert "Spring Boot" in result.missing_skills
    assert "Java" in result.existing_skills


def test_required_skills_weighted_higher_than_optional(db_session):
    _seed_base_skills(db_session)
    career = _make_career(db_session, "Backend Developer", required=["Java"], optional=["Testing"])
    profile_missing_required = _make_profile_with_skills(db_session, ["Testing"])

    result = calculate_skill_gap(profile_missing_required.id, career, db_session)
    # 1 optional matched (weight 1) out of total weight 3 (required=2 + optional=1)
    assert result.match_score < 50.0


def test_recommend_careers_sorted_descending(db_session):
    _seed_base_skills(db_session)
    _make_career(db_session, "Backend Developer", required=["Java", "Git", "SQL", "Spring Boot"])
    _make_career(db_session, "QA Engineer", required=["Testing"])
    profile = _make_profile_with_skills(db_session, ["Testing", "Java"])

    results = recommend_careers(profile.id, db_session)
    scores = [r.match_score for r in results]
    assert scores == sorted(scores, reverse=True)
