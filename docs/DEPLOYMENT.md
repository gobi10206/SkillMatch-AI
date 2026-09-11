# Deployment — SkillMatch AI

## Local development (recommended)

```bash
cp .env.example .env
docker compose up
cd backend && alembic upgrade head && python -m app.seed
```

- Frontend: http://localhost:5173
- API + docs: http://localhost:8000/docs

## Local development without Docker

See the Quick Start section in the root `README.md`.

## Production architecture (reference)

```
Cloud Load Balancer (TLS termination)
        ↓
Frontend (static build served via CDN/Nginx)
        ↓
API Gateway / reverse proxy
        ↓
FastAPI (multiple stateless replicas)
        ↓
PostgreSQL (managed, with pgvector) + Redis (managed)
        ↓
Background workers (Celery, for async resume/embedding processing)
```

- **Frontend**: `npm run build` produces a static bundle deployable
  to any static host or CDN (Netlify, Vercel, S3+CloudFront, etc.).
- **Backend**: the provided `Dockerfile` runs `uvicorn`; behind a
  process manager or container orchestrator, front it with a reverse
  proxy that terminates TLS (this repo does not configure TLS itself).
- **Database**: any managed Postgres with the `pgvector` extension
  available (e.g. via a Postgres 15+ instance where you can
  `CREATE EXTENSION vector`).
- **Workers**: Celery is listed in `requirements.txt` for background
  resume/embedding processing at scale; wiring a worker entrypoint is
  a follow-up once request volume warrants moving that work off the
  request/response cycle.

## Environment variables

See `.env.example` at the project root — every variable the backend
reads is documented there with a placeholder value. Never commit a
real `.env`.

## No paid service is required for the demo

`DEMO_MODE=true` plus `python -m app.seed` gives a fully functional
local demo — sample skills, careers, courses, and demo-labeled jobs —
with no external paid API calls anywhere in the request path.

## Scaling notes (do this only once the MVP works — Phase 44 rule)

- FastAPI processes are stateless — horizontal scaling is just
  running more replicas behind a load balancer.
- Add Redis-backed caching for expensive read paths (career/job
  matching) once traffic patterns justify it.
- Add a background worker for embedding generation on skill/career/
  job/course creation instead of computing inline, once catalog size
  grows.
