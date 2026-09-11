"""
Profile completion percentage — a simple, transparent weighted
checklist rather than a black-box score, consistent with the
project's "every score must have an explanation" rule.
"""
from app.models.profiles import Profile

WEIGHTS = {
    "headline": 10,
    "bio": 10,
    "location": 5,
    "target_career": 15,
    "experience": 25,
    "education": 15,
    "project": 10,
    "skill": 10,
}


def calculate_completion(profile: Profile) -> int:
    score = 0
    if profile.headline:
        score += WEIGHTS["headline"]
    if profile.bio:
        score += WEIGHTS["bio"]
    if profile.location:
        score += WEIGHTS["location"]
    if profile.target_career_id:
        score += WEIGHTS["target_career"]
    if profile.experiences:
        score += WEIGHTS["experience"]
    if profile.education:
        score += WEIGHTS["education"]
    if profile.projects:
        score += WEIGHTS["project"]
    if profile.user_skills:
        score += WEIGHTS["skill"]
    return min(score, 100)
