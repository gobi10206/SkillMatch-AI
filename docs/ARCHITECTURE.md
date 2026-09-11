# Architecture — SkillMatch AI

## System overview

```
[React/TS PWA] → [FastAPI] → [PostgreSQL + pgvector]
                            → [Redis: cache/queue]
                            → [AI pipeline: spaCy/sentence-transformers]
```

The backend is one FastAPI application, organized as independent
domain modules (`app/api/*` for routes, `app/services/*` and
`app/matching/*`/`app/ai/*`/`app/fairness/*`/`app/analytics/*` for
logic) that share a database but have no hidden coupling — each
module could be extracted into its own microservice later without a
rewrite, which is why routers only ever import from `app.models`,
`app.core`, and their own service layer.

## Request flow (example: job matching)

```
Client → POST /jobs/match → app/api/jobs.py
       → app/matching/job_matching.match_jobs_for_profile()
       → reads UserSkill + JobSkill (competency data only)
       → writes/updates app.models.jobs.Match (cached result)
       → returns explainable JobMatchOut[] to client
```

## Why a modular monolith, not microservices, for the MVP

Running one FastAPI process avoids the operational overhead
(service discovery, distributed tracing, inter-service auth) that
would slow down a hackathon/college-project timeline without adding
real value at this scale. The module boundaries in the codebase are
kept clean specifically so that migrating to microservices later —
e.g. splitting `app/ai` and `app/matching` into their own deployable
services behind the same API contracts — is a refactor, not a
rewrite.

## Data flow: resume → verified skill

```
Upload/paste → app/services/resume_parser.py (text extraction)
             → app/ai/skill_extraction.py (keyword + semantic match)
             → API returns ai_inferred candidates with evidence
             → user reviews (frontend ResumeAnalyzer page)
             → POST /skills/verify → UserSkill rows created/updated
               as user_verified
```

See `AI_PIPELINE.md` for the extraction pipeline in detail,
`DATABASE.md` for schema, `FAIRNESS.md` for the isolation guarantees,
`SECURITY.md` for the auth/authorization model, and
`API_DOCUMENTATION.md` for the full endpoint list.
