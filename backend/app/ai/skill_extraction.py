"""
Skill extraction pipeline (Phase 7/8/12 of the roadmap).

Approach, in order of preference:
  1. Exact/synonym match against the Skill taxonomy (fast, precise).
  2. Embedding similarity against Skill descriptions/names, for
     phrases that don't literally contain a known synonym — this is
     what lets "helped customers troubleshoot laptop issues" surface
     "Technical Support" even without the word "support" appearing.

Every extracted skill is returned with:
  - the source text span that triggered it (for SkillEvidence)
  - a confidence score
  - method: "keyword" | "semantic"
so the API layer can label results ai_inferred and show the user
*why* each skill was suggested (Phase 23, explainable AI).

This is intentionally a transparent, inspectable pipeline rather than
a single opaque model call — appropriate for a college/hackathon
project where the extraction logic itself needs to be explainable in
a viva.
"""
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.ai.embeddings import embed_text, cosine_similarity
from app.models.skills import Skill

SEMANTIC_MATCH_THRESHOLD = 0.55


@dataclass
class ExtractedSkill:
    skill_id: str
    skill_name: str
    confidence: float
    method: str  # keyword | semantic
    evidence_text: str


def _sentences(text: str) -> list[str]:
    # Simple sentence split; good enough for resume lines/short narratives
    # without pulling in a full NLP sentence tokenizer for the MVP.
    return [s.strip() for s in re.split(r"[.\n]", text) if s.strip()]


def _keyword_match(sentence: str, skills: list[Skill]) -> list[ExtractedSkill]:
    lower = sentence.lower()
    matches = []
    for skill in skills:
        terms = [skill.name.lower()]
        if skill.synonyms:
            terms += [t.strip().lower() for t in skill.synonyms.split(",") if t.strip()]
        for term in terms:
            if term and term in lower:
                matches.append(ExtractedSkill(
                    skill_id=str(skill.id), skill_name=skill.name,
                    confidence=0.9, method="keyword", evidence_text=sentence,
                ))
                break
    return matches


def _semantic_match(sentence: str, skills: list[Skill]) -> list[ExtractedSkill]:
    sentence_vec = embed_text(sentence)
    if sentence_vec is None:
        return []  # embedding model unavailable — keyword-only for this run
    matches = []
    for skill in skills:
        if not skill.embedding:
            continue
        sim = cosine_similarity(sentence_vec, list(skill.embedding))
        if sim >= SEMANTIC_MATCH_THRESHOLD:
            matches.append(ExtractedSkill(
                skill_id=str(skill.id), skill_name=skill.name,
                confidence=round(sim, 2), method="semantic", evidence_text=sentence,
            ))
    return matches


def extract_skills(text: str, db: Session) -> list[ExtractedSkill]:
    """
    Run the full pipeline over a block of text (resume text or an
    informal-experience description) and return deduplicated
    extracted skills, keeping the highest-confidence match per skill.
    """
    skills = db.query(Skill).all()
    if not skills:
        return []

    best_by_skill: dict[str, ExtractedSkill] = {}
    for sentence in _sentences(text):
        for match in _keyword_match(sentence, skills) + _semantic_match(sentence, skills):
            existing = best_by_skill.get(match.skill_id)
            if not existing or match.confidence > existing.confidence:
                best_by_skill[match.skill_id] = match

    return sorted(best_by_skill.values(), key=lambda m: m.confidence, reverse=True)
