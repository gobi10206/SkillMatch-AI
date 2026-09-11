"""
Import every model module here so `Base.metadata` is fully populated
for Alembic's `--autogenerate` and for `Base.metadata.create_all()`
in tests.
"""
from app.models.users import User, AuditLog  # noqa: F401
from app.models.profiles import Profile, Experience, Education, Project  # noqa: F401
from app.models.skills import Skill, UserSkill, SkillEvidence  # noqa: F401
from app.models.careers import Career, CareerSkill  # noqa: F401
from app.models.jobs import Company, Job, JobSkill, Application, Match  # noqa: F401
from app.models.learning import (  # noqa: F401
    Course, CourseSkill, Certification, LearningPath, LearningModule, LearningProgress
)
from app.models.fairness import FairnessSurvey, FairnessMetric  # noqa: F401
