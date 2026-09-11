# API Documentation — SkillMatch AI

Full interactive docs (auto-generated from Pydantic schemas) are
available at `/docs` (Swagger UI) and `/redoc` once the backend is
running. This file is a stable, human-readable reference.

Auth: send `Authorization: Bearer <access_token>` on any endpoint
marked 🔒. Get a token from `POST /auth/login`.

## Auth (`/auth`)

| Method & Path | Auth | Description |
|---|---|---|
| POST `/auth/register` | — | Create an account (job_seeker/employer/admin) |
| POST `/auth/login` | — | Returns `{access_token, refresh_token}` |
| POST `/auth/refresh` | — | Exchange a refresh token for a new pair |
| GET `/auth/me` | 🔒 | Current user |

## Profile (`/profile`)

| Method & Path | Auth | Description |
|---|---|---|
| GET `/profile` | 🔒 | Own profile with experiences/education/projects |
| PUT `/profile` | 🔒 | Update headline/bio/location/target career |
| POST `/profile/experiences` | 🔒 | Add a formal/informal/volunteer/freelance experience |
| POST `/profile/education` | 🔒 | Add an education record |
| POST `/profile/projects` | 🔒 | Add a project |

## Resume (`/resume`)

| Method & Path | Auth | Description |
|---|---|---|
| POST `/resume/analyze` | 🔒 | Extract skills from pasted resume text |
| POST `/resume/upload` | 🔒 | Extract skills from an uploaded PDF/DOCX (multipart) |

## Skills (`/skills`)

| Method & Path | Auth | Description |
|---|---|---|
| GET `/skills` | — | Browse the skill taxonomy, optional `?category=` |
| POST `/skills/extract-informal` | 🔒 | Extract skills from an informal-experience description |
| POST `/skills/verify` | 🔒 | Accept/reject/edit AI-inferred skills → saves as user_verified |
| GET `/skills/mine` | 🔒 | List the current user's saved skills |

## Career (`/career`)

| Method & Path | Auth | Description |
|---|---|---|
| GET `/career` | — | List all careers |
| GET `/career/recommend` | 🔒 | Top career matches for the current profile |
| GET `/career/{id}/skill-gap` | 🔒 | Existing vs. missing skills for one career |
| GET `/career/{id}/readiness` | 🔒 | Career readiness score with component breakdown |

## Learning (`/learning`)

| Method & Path | Auth | Description |
|---|---|---|
| POST `/learning/path/{career_id}` | 🔒 | Generate/regenerate a learning path |
| GET `/learning/path/{career_id}` | 🔒 | Fetch a path with progress |
| GET `/learning/progress` | 🔒 | All learning paths for the current profile |
| PUT `/learning/modules/{id}/progress` | 🔒 | Update a module's completion status |

## Jobs & Internships

| Method & Path | Auth | Description |
|---|---|---|
| GET `/jobs` | — | Browse full-time jobs, filters: location, is_remote, experience_level |
| GET `/internships` | — | Same filters, internship postings only |
| POST `/jobs/match` | 🔒 | Explainable job matches for the current profile |
| POST `/jobs` | 🔒 employer | Create a job posting |

## Applications (`/applications`)

| Method & Path | Auth | Description |
|---|---|---|
| GET `/applications` | 🔒 | List the current user's tracked applications |
| POST `/applications` | 🔒 | Save/apply to a job |
| PUT `/applications/{id}` | 🔒 | Move an application through the Kanban statuses |

## Employer (`/employer`)

| Method & Path | Auth | Description |
|---|---|---|
| POST `/employer/company` | 🔒 employer | Create a company profile |
| GET `/employer/candidates/search` | 🔒 employer | Search candidates by skill names only |

## Analytics (`/analytics`) — public, aggregated only

| Method & Path | Description |
|---|---|
| GET `/analytics/skills/demand` | Most-demanded skills across careers |
| GET `/analytics/skills/gaps` | Skills required but rarely held |
| GET `/analytics/careers/popular` | Careers with the most active learners |

## Admin (`/admin`)

| Method & Path | Auth | Description |
|---|---|---|
| GET `/admin/users` | 🔒 admin | List all users |
| PUT `/admin/users/{id}/deactivate` | 🔒 admin | Disable an account |
| PUT `/admin/jobs/{id}/flag` | 🔒 admin | Deactivate a flagged job posting |
| GET `/admin/fairness` | 🔒 admin | Fairness dashboard metrics |

## System

| Method & Path | Description |
|---|---|
| GET `/health` | Liveness probe |
| GET `/health/ready` | Readiness probe |

## Errors

All error responses follow FastAPI's standard shape:
```json
{ "detail": "human-readable message" }
```
Validation errors (422) include per-field detail from Pydantic.
