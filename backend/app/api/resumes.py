"""
Resume endpoints: upload a file or paste text, run the extraction
pipeline, and return AI-inferred skills for the user to review
(nothing is written to user_skills until POST /skills/verify — see
Phase 11 rule: "user must review and correct AI-extracted skills
before they become part of their profile").
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.users import User
from app.ai.skill_extraction import extract_skills
from app.services.resume_parser import extract_text, UnsupportedFileError
from app.schemas.skills import ResumeAnalyzeIn, ResumeAnalyzeOut, ExtractedSkillOut

router = APIRouter()


@router.post("/analyze", response_model=ResumeAnalyzeOut)
def analyze_pasted_text(payload: ResumeAnalyzeIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    extracted = extract_skills(payload.resume_text, db)
    return ResumeAnalyzeOut(
        extracted_text_preview=payload.resume_text[:500],
        extracted_skills=[ExtractedSkillOut(**e.__dict__) for e in extracted],
    )


@router.post("/upload", response_model=ResumeAnalyzeOut)
async def upload_resume(
    file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    file_bytes = await file.read()
    try:
        text = extract_text(file_bytes, file.content_type)
    except UnsupportedFileError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract any text from this file")

    extracted = extract_skills(text, db)
    return ResumeAnalyzeOut(
        extracted_text_preview=text[:500],
        extracted_skills=[ExtractedSkillOut(**e.__dict__) for e in extracted],
    )
