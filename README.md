# SkillMatch AI

Inclusive Workforce Upskilling & Career Path Engine — SDG 4, 8, 10.

## Status

Core platform implemented end-to-end: auth, profiles, resume/skill
extraction with user review, career recommendation, skill-gap and
readiness scoring, personalized learning paths, job/internship
matching, fairness-isolated architecture with an admin dashboard,
employer portal, community analytics, demo-mode seed data, automated
backend tests, and full documentation set in `docs/`.

Frontend ships the core loop (Landing, Register, Login, Resume
Analyzer, Dashboard) wired to the live API; deeper pages (Career
Explorer, Employer Dashboard, Admin UI, Application Kanban board) are
implemented on the backend and ready for additional frontend screens
as a natural next iteration.

## Quick Start (Docker)

```bash
cp .env.example .env
docker compose up -d
cd backend && alembic upgrade head && python -m app.seed
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Demo admin login: `admin@skillmatch.demo` / `ChangeMe123!`
- Demo employer login: `employer@skillmatch.demo` / `ChangeMe123!`

## Running backend tests

```bash
cd backend
pip install -r requirements.txt --break-system-packages
pytest
```

## Documentation

See `docs/`: `ARCHITECTURE.md`, `DATABASE.md`, `AI_PIPELINE.md`,
`FAIRNESS.md`, `SECURITY.md`, `API_DOCUMENTATION.md`,
`DEPLOYMENT.md`, `DEMO_GUIDE.md`, `SDG_IMPACT.md`,
`COLLEGE_PROJECT_REPORT.md`, `PRESENTATION_OUTLINE.md`,
`VIVA_PREPARATION.md`.

## Quick Start (without Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
skillmatch-ai/
├── frontend/   # React + TypeScript + Vite + Tailwind (PWA)
├── backend/    # FastAPI + SQLAlchemy + Pydantic
├── data/       # demo/sample datasets (clearly labeled, never real market data)
├── ml/         # models, notebooks, embedding/matching pipelines
├── docs/       # architecture, API, fairness, security, demo docs
└── scripts/    # setup/maintenance scripts
```

## Demo Mode

The app runs fully offline with `DEMO_MODE=true` using seeded sample
users, resumes, careers, jobs, and courses — no paid APIs required.
Demo data is always visibly labeled as such in the UI.
