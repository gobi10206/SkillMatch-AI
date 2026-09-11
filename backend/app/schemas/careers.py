"""Schemas for career recommendation, skill-gap, readiness, and learning-path endpoints."""
import uuid

from pydantic import BaseModel


class CareerOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    industry: str | None

    class Config:
        from_attributes = True


class SkillGapOut(BaseModel):
    career_id: uuid.UUID
    career_title: str
    match_score: float
    existing_skills: list[str]
    missing_skills: list[str]
    explanation: str


class ReadinessOut(BaseModel):
    overall_pct: float
    technical_skills_pct: float
    projects_pct: float
    certifications_pct: float
    experience_pct: float
    explanation: str


class LearningModuleOut(BaseModel):
    id: uuid.UUID
    sequence: int
    skill_name: str
    learning_objective: str | None
    estimated_effort_hours: int | None
    recommended_course_title: str | None
    status: str
    completion_pct: int


class LearningPathOut(BaseModel):
    id: uuid.UUID
    career_title: str
    estimated_weeks_min: int | None
    estimated_weeks_max: int | None
    is_estimate: bool = True
    modules: list[LearningModuleOut]


class ProgressUpdateIn(BaseModel):
    status: str  # not_started | in_progress | completed
    completion_pct: int
