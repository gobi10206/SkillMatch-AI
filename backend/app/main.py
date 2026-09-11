"""
SkillMatch AI — FastAPI application entrypoint.

Wires together the API routers for each domain module and exposes
health-check endpoints used by orchestration/monitoring.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="SkillMatch AI API",
    description="Inclusive Workforce Upskilling & Career Path Engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health():
    """Liveness probe — process is up."""
    return {"status": "ok"}


@app.get("/health/ready", tags=["system"])
def health_ready():
    """
    Readiness probe — placeholder until DB/Redis connectivity checks
    are wired in during Phase 3 (database) and Phase 4 (auth).
    """
    return {"status": "ready", "checks": {"database": "not_wired_yet"}}


from app.api import auth, profiles, resumes, skills, careers, learning, jobs, applications, employer, analytics, admin

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profiles.router, prefix="/profile", tags=["profile"])
app.include_router(resumes.router, prefix="/resume", tags=["resume"])
app.include_router(skills.router, prefix="/skills", tags=["skills"])
app.include_router(careers.router, prefix="/career", tags=["career"])
app.include_router(learning.router, prefix="/learning", tags=["learning"])
app.include_router(jobs.router, tags=["jobs"])  # defines its own /jobs and /internships prefixes
app.include_router(applications.router, prefix="/applications", tags=["applications"])
app.include_router(employer.router, prefix="/employer", tags=["employer"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
