"""Schemas for jobs/internships browsing, employer job creation, and application tracking."""
import uuid
from datetime import date

from pydantic import BaseModel


class JobSkillIn(BaseModel):
    skill_id: uuid.UUID
    is_required: bool = True


class JobCreate(BaseModel):
    title: str
    description: str | None = None
    job_type: str = "full_time"  # full_time | internship
    location: str | None = None
    is_remote: bool = False
    experience_level: str | None = None
    stipend_or_salary_note: str | None = None
    required_skills: list[JobSkillIn] = []


class JobOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    job_type: str
    location: str | None
    is_remote: bool
    experience_level: str | None
    stipend_or_salary_note: str | None
    is_demo_data: bool

    class Config:
        from_attributes = True


class JobMatchOut(BaseModel):
    job_id: uuid.UUID
    job_title: str
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str


class ApplicationCreate(BaseModel):
    job_id: uuid.UUID
    status: str = "saved"


class ApplicationUpdate(BaseModel):
    status: str
    applied_on: date | None = None


class ApplicationOut(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    job_title: str
    status: str
    applied_on: date | None

    class Config:
        from_attributes = True


class CompanyCreate(BaseModel):
    name: str
    description: str | None = None
    website: str | None = None
