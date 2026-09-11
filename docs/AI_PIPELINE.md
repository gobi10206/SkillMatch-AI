# AI / NLP Pipeline — SkillMatch AI

## Pipeline stages

```
Resume file / pasted text / informal-experience text
  → app/services/resume_parser.py     (pdfplumber / python-docx text extraction)
  → app/ai/skill_extraction.py        (sentence split → keyword match → semantic match)
  → API layer                          (returns ai_inferred candidates + evidence + confidence)
  → user review (accept/reject/edit)   (frontend ResumeAnalyzer page)
  → POST /skills/verify                (user_verified UserSkill rows created)
```

## Skill extraction: two matching methods

1. **Keyword/synonym match** — checks each sentence against the
   `Skill.name` and `Skill.synonyms` fields in the taxonomy.
   Fast, precise, no ML dependency, confidence fixed at 0.9.

2. **Semantic match** — embeds each sentence with
   `sentence-transformers/all-MiniLM-L6-v2` (384-dim) and compares it
   by cosine similarity against precomputed `Skill.embedding` vectors,
   using a 0.55 similarity threshold. This is what lets phrases like
   "helped customers troubleshoot laptop issues" surface "Technical
   Support" even when no listed synonym literally appears.

Both methods run over every sentence; the highest-confidence match
per skill wins. Every result carries the source sentence as evidence,
which becomes a `SkillEvidence` row — the basis for explainability.

## Why this two-method design, not a single LLM call

A transparent, inspectable pipeline is more appropriate than an
opaque single-model call for a system that has to explain *why* each
skill was suggested (Phase 23) and that a student needs to defend in
a viva. Keyword matching alone misses paraphrased language; semantic
matching alone can be too permissive on short, ambiguous text. Using
both and keeping the higher-confidence match per skill balances
precision and recall while staying explainable end-to-end.

## Embeddings and vector search

`app/ai/embeddings.py` wraps `sentence-transformers`, loading the
model lazily so environments that never touch AI features (most
tests) don't pay the startup cost. If the model can't load (e.g. not
downloaded, offline CI), `embed_text()` returns `None` and callers
fall back to keyword-only matching rather than crashing — see
`_semantic_match()` in `skill_extraction.py`.

Embeddings are stored via `app/core/vector_type.py`'s `PortableVector`
type: real `pgvector` columns on Postgres, a JSON-encoded fallback on
SQLite so the test suite doesn't require a live Postgres instance.
Production similarity search (career/job/course matching against a
user's skill embeddings) is designed to use pgvector's indexed
similarity operators once embeddings are populated for all taxonomy
rows — see the `embed_batch()` helper for bulk population.

## Explainability

Every AI output carries a label — `ai_inferred`, `user_verified`,
`estimated`, or `external` — and every score (career match, job
match, career readiness) is computed from an inspectable formula with
an `explanation` string, never a black-box number. See
`app/services/career_recommendation.py`,
`app/services/career_readiness.py`, and `app/matching/job_matching.py`.

## Feedback loop

`POST /skills/verify` implements the accept/reject/edit flow (Phase
38). Per the project rule, feedback is stored (as `user_verified`
UserSkill rows) but does **not** automatically retrain any model —
there is no production retraining pipeline in this MVP, only the
verified-skill signal available for a future, explicitly-triggered
retraining/taxonomy-improvement process.
