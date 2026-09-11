# Fairness — SkillMatch AI

## Principle

Matching and ranking (career recommendations, job matches, employer
candidate search) use **only** competency data: verified/inferred
skills, experience, education, and job/career requirements. No
protected characteristic — race, religion, gender, caste, disability,
political affiliation, or any other — is ever an input to a ranking
or scoring function.

## How this is enforced, not just stated

- **Schema isolation**: `FairnessSurvey` (voluntary demographic data)
  is a separate table linked to the rest of the schema only by
  `user_id`. No ranking table (`matches`, `user_skills`,
  `career_skills`, `job_skills`) has a foreign key to or from it.
- **Code isolation**: `app/matching/job_matching.py` and
  `app/services/career_recommendation.py` never import
  `FairnessSurvey`. This is checked directly by
  `tests/test_job_matching.py::test_matching_module_never_imports_fairness_survey`,
  which fails the build if that ever changes.
- **API contract**: employer candidate search
  (`GET /employer/candidates/search`) accepts only a list of skill
  names — there is no demographic filter parameter to even request.

## Fairness dashboard (admin-only)

`GET /admin/fairness` (implemented in `app/api/admin.py` and
`app/fairness/metrics.py`) computes aggregated, group-level
statistics — e.g. selection-rate parity — from consented survey data
joined against match outcomes, for measurement only. Groups smaller
than `MIN_GROUP_SIZE` (10) are excluded from published metrics to
avoid re-identification. The dashboard response always includes:

- `data_used` — exactly what fed the metric
- `data_not_used` — the explicit list of protected characteristics
  that never enter ranking
- `limitations` — plain-language caveats

## Terminology

This system describes itself as **fairness-aware** and
**bias-mitigated** — never "bias-free." No automated system can
certify the complete absence of bias, and claiming otherwise would
overstate what aggregated, small-sample statistics can actually show.

## Limitations

- Demographic data collection is voluntary and opt-in; fairness
  metrics only cover users who consented, so they are not a complete
  picture of the full user base.
- The MVP's `FairnessSurvey.demographic_data` field is a placeholder
  (opaque blob) — the specific fields to collect are a policy
  decision for legal/compliance review before any real deployment,
  not something hard-coded into this codebase.
- Group-level statistics can still mask individual-level disparities;
  this dashboard is one signal among several a real deployment would
  need (see also `SECURITY.md` and `PRIVACY` notes in `ARCHITECTURE.md`).
