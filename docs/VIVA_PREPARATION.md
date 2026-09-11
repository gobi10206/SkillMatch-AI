# Viva Preparation - SkillMatch AI

1. Why FastAPI? Async support, automatic OpenAPI docs from Pydantic
   schemas, strong request validation, minimal boilerplate compared
   to Flask/Django for an API-first project.

2. Why PostgreSQL? Mature, free, ACID-compliant, and critically
   supports the pgvector extension so relational and vector data live
   in one store instead of two separate systems.

3. Why embeddings? They let the system match meaning, not just exact
   words - "helped customers troubleshoot laptop issues" can match
   "Technical Support" without that literal phrase appearing.

4. Why vector search (pgvector) over FAISS/ChromaDB? Simplicity for
   this project's scale: one database to run and migrate, no second
   service, transactional consistency with relational data. FAISS or
   Chroma are a documented upgrade path if the catalog grows large
   enough to need specialized ANN indexing.

5. How does skill extraction work? Two methods per sentence: exact or
   synonym keyword matching against the taxonomy, and embedding
   cosine-similarity matching (threshold 0.55) for paraphrased text.
   Highest-confidence match per skill wins. See app/ai/skill_extraction.py.

6. How is skill matching performed? A weighted-sum formula: required
   skills count double an optional skill's weight; score = matched
   weight divided by total weight times 100. Same formula shape for
   career skill gap and job matching.

7. How is skill gap calculated? Compare a profile's UserSkill set
   against a career's CareerSkill requirements; skills present in one
   but not the other are the gap, reported both ways (existing vs
   missing).

8. How does recommendation work? All careers are scored against the
   profile with the same skill-gap formula and sorted descending -
   there is no separate "recommendation model," which keeps the
   result explainable.

9. How is fairness handled? Architecturally: demographic data lives
   in a schema-isolated FairnessSurvey table never joined into
   ranking queries; a test asserts the matching module's source never
   even imports that model.

10. What are the limitations? Keyword+embedding extraction is simpler
    than a fine-tuned NER model and can miss idiomatic phrasing;
    fairness metrics only cover consenting users; no production
    retraining pipeline; several security hardening items are
    documented but not yet implemented (see SECURITY.md).

11. How is privacy protected? Minimal data collection, explicit
    consent for the fairness survey, raw resume files aren't
    persisted after extraction, secrets via environment variables only.

12. How can the system scale? Stateless FastAPI replicas behind a
    load balancer, Redis caching for expensive read paths, a
    documented (if not yet wired) Celery worker path for background
    embedding generation.

13. How can AI hallucinations be controlled? The pipeline never
    generates free-text claims about jobs, salaries, or certifications
    - it only extracts against a fixed taxonomy and computes scores
    from stored data, so there's no generative step that could
    fabricate facts. Demo data is explicitly labeled.

14. Why is this different from LinkedIn/job portals? It treats
    informal, freelance, and volunteer experience as first-class input
    to skill discovery, and every match or score is explainable by
    design, not a black box.

15. How does it support SDG 4? Personalized, step-based learning
    paths with tracked module completion.

16. How does it support SDG 8? Competency-based job/internship
    matching and a transparent career-readiness score.

17. How does it support SDG 10? Recognizes informal experience, ships
    as a low-bandwidth PWA, and measures fairness via an isolated,
    aggregated dashboard.

18. Why weighted-sum scores instead of an ML ranking model?
    Explainability was a hard requirement; a linear, inspectable
    formula lets every score come with a plain-language "why," which
    an opaque learned ranker would not.

19. How does authentication work? JWT access (30 min) plus refresh
    (7 day) tokens, bcrypt-hashed passwords, role-based route guards
    via a FastAPI dependency (require_role).

20. How do you prevent one user from seeing another's private data?
    Every profile/skill/application route resolves "current user's
    own profile" server-side from the JWT - there's no endpoint that
    accepts an arbitrary profile ID for job seekers.

21. What happens if the embedding model isn't available? embed_text()
    fails soft and returns None; the extraction pipeline falls back
    to keyword-only matching rather than crashing.

22. How are tests structured? In-memory SQLite for speed via a pytest
    fixture; vector columns use a dialect-aware type (PortableVector)
    so the same models work on SQLite in tests and real pgvector in
    production.

23. What database normalization level is used? Third normal form -
    see DATABASE.md for the full entity list and relationships.

24. How is the learning path duration estimated? A fixed per-skill
    effort estimate divided by an assumed weekly study pace, always
    surfaced as a min-max range and explicitly labeled an estimate,
    never a guarantee.

25. How is the career readiness score explained? It's a weighted sum
    of four components (technical skills, projects, certifications,
    experience) with the weights and each component's value returned
    in the API response - never a single opaque number.

26. What's stored about a resume upload? Only the extracted text and
    derived skills; the raw uploaded bytes are processed in memory
    and not persisted, per the project's data-minimization rule.

27. How does the employer candidate search stay fair? Its API
    contract only accepts skill-name filters - there's no parameter
    that could carry a demographic filter even if someone tried.

28. What's the demo-mode guarantee? Every seeded job/course row is
    flagged is_demo_data=True so the UI can label it, and no external
    paid API is called anywhere in the seed script or request path.

29. How would you extend this to microservices? The app/ai,
    app/matching, app/fairness, and app/analytics modules only depend
    on app.models/app.core - they're structured so each could become
    its own service behind the same API contract without a rewrite.

30. What's the single biggest architectural decision and why?
    Choosing transparent, formula-based scoring over opaque ML models
    for every user-facing number - it's slightly less sophisticated
    but directly satisfies the explainability requirement that runs
    through the whole spec.
