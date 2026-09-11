# Hackathon Demo Guide — SkillMatch AI

Target: 5-7 minutes. All data referenced below is demo-mode data,
visibly labeled as such in the UI (is_demo_data=True on jobs/courses).

## Setup (before you present)

```bash
docker compose up -d
cd backend && alembic upgrade head && python -m app.seed
```

Confirm /health returns {"status": "ok"} and the frontend loads at
localhost:5173.

## Script

1. Register a new job-seeker account on the Landing -> Register page.
2. Describe an informal experience on the Resume Analyzer page:
   "I helped my family's business manage inventory and customer billing."
3. Show AI-detected transferable skills - point out the evidence
   snippet and confidence shown next to each suggested skill, and that
   nothing saves until you click "Save Reviewed Skills" (explainability
   plus user control, not silent inference).
4. Select target career "Software Developer" (or another seeded
   career) from the Career Explorer.
5. Show the skill gap card: existing vs missing skills, plain-language
   explanation.
6. Generate the personalized learning path - point out the estimated
   week range is explicitly framed as an estimate.
7. Open Job Matches on the dashboard - show the explainable match
   card (matched vs missing skills, plain-language "why this job
   matches you").
8. Open the Fairness dashboard (admin login: admin@skillmatch.demo /
   ChangeMe123! from the seed script) - show data_used / data_not_used
   / limitations in the response, and narrate the schema-isolation
   guarantee (FairnessSurvey is never joined into ranking).
9. Return to the Dashboard - profile completion, career readiness
   breakdown, job match count.
10. Close on the SDG tie-in: SDG 4 (learning modules completed),
    SDG 8 (job/internship matches, career readiness), SDG 10
    (accessibility, low-bandwidth PWA, fairness metrics).

## Fallback if live demo breaks

Have `docker compose logs backend` open in a second terminal. The
seed script is idempotent-safe to re-run (it no-ops if skills already
exist), so re-running migrations/seed is a fast recovery path mid-demo
if the DB gets into a bad state.
