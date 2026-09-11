# Security — SkillMatch AI

## Authentication

- Passwords hashed with bcrypt (`passlib`), never stored or logged
  in plaintext (`app/core/security.py`).
- JWT access tokens (30 min default) and refresh tokens (7 days
  default), `HS256`, signed with `SECRET_KEY` from environment —
  never hard-coded, never committed (`.env` is git-ignored).
- `POST /auth/refresh` rotates a refresh token into a new access/
  refresh pair without re-sending credentials.

## Authorization

- `app/api/deps.py::require_role()` is a dependency factory used on
  every employer/admin-only route (job posting, company creation,
  candidate search, all `/admin/*` routes). A `job_seeker` token
  cannot call these — FastAPI returns `403` before any handler code
  runs.
- Every profile/skill/application route operates only on the
  **current user's own** data — there is no "get profile by
  arbitrary id" endpoint for job seekers, preventing one user from
  reading another's data via ID guessing.

## Input & file validation

- Pydantic schemas validate every request body (type, length, enum
  membership like `role` and application `status`).
- Resume uploads (`app/services/resume_parser.py`) are restricted to
  an explicit content-type allowlist (`PDF`, `DOCX`) and a 5MB size
  cap, checked before any parsing happens.
- Uploaded file bytes are processed in memory and not persisted to
  disk or the database by default (see Phase 37 rule in
  `AI_PIPELINE.md`).

## Transport & headers

- CORS is restricted to `settings.cors_origins` (configured per
  environment via `.env`), not wildcarded.
- Rate limiting on auth/upload endpoints is a documented requirement
  for production deployment; the MVP ships without a specific rate
  limiter wired in — add one (e.g. `slowapi`) before any public
  deployment. This is called out explicitly rather than silently
  assumed.

## Secrets

- `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL` all come from environment
  variables via `app/core/config.py`. `.env.example` documents every
  variable with placeholder values; the real `.env` is never
  committed (`.gitignore`).

## Audit logging

- `AuditLog` (`app/models/users.py`) is available for recording
  sensitive actions (login, role changes, admin overrides). Wiring
  every sensitive action to write an audit row is a straightforward
  follow-up once the core flows are validated — the table and model
  are ready now so that work doesn't require a schema change later.

## Known gaps to close before any real deployment

- No rate limiting wired in yet (see above).
- No email verification flow yet (`User.is_verified` field exists but
  nothing sets it to `True` outside manual admin action).
- No malware/antivirus scanning on uploaded files — only type/size
  validation. Add a scanning step (e.g. ClamAV) before production use.
- No HTTPS/TLS termination configured here — that's the responsibility
  of whatever reverse proxy/load balancer fronts the deployment (see
  `DEPLOYMENT.md`).
