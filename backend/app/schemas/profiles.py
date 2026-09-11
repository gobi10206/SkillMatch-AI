"""Request/response schemas for profile and its sub-records."""
import uuid
from datetime import date

from pydantic import BaseModel


class ExperienceIn(BaseModel):
    title: str
    organization: str | None = None
    experience_type: str = "formal"  # formal | informal | volunteer | freelance
    description: str
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False


class ExperienceOut(ExperienceIn):
    id: uuid.UUID

    class Config:
        from_attributes = True


class EducationIn(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class EducationOut(EducationIn):
    id: uuid.UUID

    class Config:
        from_attributes = True


class ProjectIn(BaseModel):
    title: str
    description: str | None = None
    url: str | None = None


class ProjectOut(ProjectIn):
    id: uuid.UUID

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    headline: str | None = None
    bio: str | None = None
    location: str | None = None
    target_career_id: uuid.UUID | None = None


class ProfileOut(BaseModel):
    id: uuid.UUID
    headline: str | None
    bio: str | None
    location: str | None
    target_career_id: uuid.UUID | None
    profile_completion_pct: int
    experiences: list[ExperienceOut] = []
    education: list[EducationOut] = []
    projects: list[ProjectOut] = []

    class Config:
        from_attributes = True
