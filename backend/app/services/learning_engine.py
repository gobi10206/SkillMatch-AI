"""
Personalized learning path generation (Phase 16). Builds one
LearningModule per missing skill, in a fixed sensible order
(required skills before optional ones), each pointing at a matching
Course when one exists in the catalog. Estimated durations are
clearly framed as estimates, never guarantees (Phase 13 rule).
"""
from sqlalchemy.orm import Session

from app.models.careers import Career, CareerSkill
from app.models.learning import LearningPath, LearningModule, Course, CourseSkill
from app.models.skills import UserSkill

DEFAULT_EFFORT_HOURS_PER_SKILL = 12  # rough estimate, surfaced to the user as such


def generate_learning_path(profile_id, career: Career, db: Session) -> LearningPath:
    user_skill_ids = {
        us.skill_id for us in db.query(UserSkill).filter(UserSkill.profile_id == profile_id).all()
    }
    career_skills = (
        db.query(CareerSkill)
        .filter(CareerSkill.career_id == career.id, ~CareerSkill.skill_id.in_(user_skill_ids))
        .order_by(CareerSkill.is_required.desc())
        .all()
    )

    existing_path = db.query(LearningPath).filter(
        LearningPath.profile_id == profile_id, LearningPath.career_id == career.id
    ).first()
    if existing_path:
        db.query(LearningModule).filter(LearningModule.learning_path_id == existing_path.id).delete()
        path = existing_path
    else:
        path = LearningPath(profile_id=profile_id, career_id=career.id)
        db.add(path)
        db.flush()

    total_hours = 0
    for i, cs in enumerate(career_skills, start=1):
        course = (
            db.query(Course)
            .join(CourseSkill, CourseSkill.course_id == Course.id)
            .filter(CourseSkill.skill_id == cs.skill_id)
            .first()
        )
        effort = DEFAULT_EFFORT_HOURS_PER_SKILL
        total_hours += effort
        db.add(LearningModule(
            learning_path_id=path.id,
            skill_id=cs.skill_id,
            sequence=i,
            learning_objective=f"Build working proficiency in {cs.skill.name}",
            estimated_effort_hours=effort,
            recommended_course_id=course.id if course else None,
        ))

    # ~20 effective learning hours/week assumed for the estimate range
    path.estimated_weeks_min = max(1, round(total_hours / 25))
    path.estimated_weeks_max = max(path.estimated_weeks_min, round(total_hours / 15))

    db.commit()
    db.refresh(path)
    return path
