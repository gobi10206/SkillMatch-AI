# College Project Report Material - SkillMatch AI

## Abstract

SkillMatch AI is a full-stack, AI-powered platform that helps job
seekers discover skills from both formal and informal experience,
identify gaps against a target career, receive a personalized
learning path, and get matched to explainable job/internship
opportunities - all through a fairness-aware, transparent scoring
system. It targets UN SDG 4 (Quality Education), SDG 8 (Decent Work
and Economic Growth), and SDG 10 (Reduced Inequalities).

## Introduction

Conventional job portals assume a user already knows how to describe
their skills in industry terms. This excludes people whose competency
came from informal, freelance, or volunteer work - exactly the
population SDG 10 is concerned with. SkillMatch AI's core
differentiator is treating informal experience as a first-class input
to skill extraction, not an afterthought.

## Problem Statement

Job seekers, especially from underserved backgrounds, often cannot
articulate their existing skills in a way that matches employer or
career-path requirements, and lack a clear, explainable path from
"here's what I have" to "here's what to learn and where to apply."

## Existing System

Traditional job portals: keyword search, manual skill entry, opaque
"match percentage" scores with no explanation, no support for
informal/volunteer experience, no learning-path guidance.

## Proposed System

A four-stage loop: Discover Skills -> Understand Career Potential ->
Identify Skill Gaps -> Learn -> Build Evidence -> Get Matched -> Apply
-> Track Progress, with every AI output labeled (ai_inferred vs
user_verified) and every score accompanied by a plain-language
explanation.

## Objectives

1. Extract skills from resumes and informal-experience text using a
   transparent keyword + semantic matching pipeline.
2. Compute explainable skill-gap and career-readiness scores.
3. Generate personalized, step-based learning paths.
4. Match users to jobs/internships using competency data only.
5. Enforce fairness by architecture, not just policy - demographic
   data is schema-isolated from ranking.

## Methodology

See `ARCHITECTURE.md` and `AI_PIPELINE.md` for full detail. In brief:
FastAPI + PostgreSQL/pgvector backend, React/TypeScript PWA frontend,
a two-method (keyword + embedding-similarity) skill extraction
pipeline, and transparent weighted-sum scoring for skill gap, job
match, and career readiness (never a black-box model score).

## System Architecture / Modules / Algorithms / AI-NLP Methodology / Database Design / UI Design

See the dedicated docs: `ARCHITECTURE.md`, `AI_PIPELINE.md`,
`DATABASE.md`, and the `frontend/src/pages/` implementation for UI.

## Results

A working demo covering registration through job matching, backed by
seeded demo data (clearly labeled), with automated tests covering
authentication, skill extraction, career/job matching scoring logic,
and the fairness code-isolation guarantee (see `backend/tests/`).

## Advantages

Explainable at every stage; recognizes informal/volunteer experience;
fairness enforced structurally; runs fully offline in demo mode (no
paid APIs required); modular codebase suited to incremental extension.

## Limitations

Keyword+embedding extraction is simpler than a fine-tuned NER model
and can miss highly idiomatic phrasing (see `AI_PIPELINE.md`);
fairness metrics only cover users who opt into the voluntary survey;
no production retraining pipeline; several security hardening items
(rate limiting, email verification, malware scanning) are documented
as pre-production gaps in `SECURITY.md`, not yet implemented.

## Future Scope

Fine-tuned domain-specific NER for skill extraction; real course-
catalog API integrations (clearly distinguished from demo data);
production-grade background worker pipeline for embeddings at scale;
i18n rollout beyond English; mobile-native app shell.

## SDG Alignment

See `SDG_IMPACT.md` for the full mapping and the explicit
projected-vs-measured distinction.

## Conclusion

SkillMatch AI demonstrates that an explainable, fairness-aware
skill-to-opportunity pipeline is achievable within a college-project/
hackathon timeline without sacrificing architectural rigor -
transparent scoring, schema-level fairness isolation, and honest
labeling of AI inference are treated as core requirements, not
polish.
