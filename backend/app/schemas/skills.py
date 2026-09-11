"""Schemas for resume analysis, skill extraction, and skill review."""
import uuid

from pydantic import BaseModel


class ExtractedSkillOut(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    confidence: float
    method: str
    evidence_text: str


class ResumeAnalyzeIn(BaseModel):
    resume_text: str  # for the "paste text" path; file upload uses a separate multipart route


class ResumeAnalyzeOut(BaseModel):
    extracted_text_preview: str
    extracted_skills: list[ExtractedSkillOut]


class InformalExperienceIn(BaseModel):
    description: str


class SkillReviewAction(BaseModel):
    skill_id: uuid.UUID
    action: str  # accept | reject | edit
    proficiency_level: str | None = None  # used when action == edit


class UserSkillOut(BaseModel):
    id: uuid.UUID
    skill_id: uuid.UUID
    skill_name: str
    proficiency_level: str
    source: str
    confidence_score: float | None
    is_verified: bool

    class Config:
        from_attributes = True
