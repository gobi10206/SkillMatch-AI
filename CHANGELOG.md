# Changelog

## Bug-fix pass (post-Phase 22)

This sandbox has no network/DB access, so the project could not be
executed end-to-end here. Instead of shipping unverified code, this
pass did a full manual audit of every backend module and the
frontend TypeScript files, and fixed the following real issues found
by inspection:

1. **Postgres-only UUID type used everywhere** — every model used
   `sqlalchemy.dialects.postgresql.UUID`, which cannot be compiled
   against SQLite. This would have made the entire backend test
   suite crash at table-creation time. Fixed by switching every
   model to SQLAlchemy's cross-dialect `sqlalchemy.Uuid(as_uuid=True)`,
   which renders as native `UUID` on Postgres and a compatible type
   on SQLite — no behavior change in production, tests now work.

2. **Missing `email-validator` dependency** — `pydantic.EmailStr` (used
   in auth schemas) requires this optional package; it wasn't in
   `requirements.txt` and would raise an ImportError the first time
   any request touched an email field. Added
   `email-validator==2.2.0`.

3. **Unpinned `bcrypt` breaks `passlib`** — `passlib==1.7.4` reads a
   `bcrypt.__about__.__version__` attribute that was removed in
   `bcrypt>=4.1.0`, causing password hashing to crash at runtime.
   Pinned `bcrypt==4.0.1`, a known-compatible version.

4. **Deprecated `pydantic-settings` config style** — `app/core/config.py`
   used the legacy nested `class Config`. Switched to
   `model_config = SettingsConfigDict(...)`, the current API.

5. **SQLite in-memory test DB not thread-safe with `TestClient`** —
   the pytest `db_session` fixture created a plain
   `sqlite:///:memory:` engine. FastAPI's `TestClient` can dispatch a
   request onto a different thread than the one that set up the
   fixture, and SQLite's default per-thread connection pooling would
   hand that request a fresh, empty in-memory database, causing
   `no such table` errors on every API-level test. Fixed by adding
   `poolclass=StaticPool` so the whole test run shares one
   connection.

6. **Frontend: `React.FormEvent` used without importing `React`** —
   `Login.tsx` and `Register.tsx` referenced the `React` namespace
   for a type annotation without a default import, which fails
   `tsc -b` (the type-checked production build), even though the
   unchecked dev server might not catch it. Fixed by importing
   `type FormEvent` directly from `react` instead.

7. **Explicit `Date` type on `Application.applied_on`** — this column
   relied on SQLAlchemy 2.0's implicit type inference from the `date`
   annotation; made the `Date` type explicit to remove any doubt,
   consistent with every other date column in the schema.

None of these were caught by the earlier `python -m py_compile`
checks, since compilation only catches syntax errors — all seven are
either import-time/runtime errors or issues that only surface once
the app actually talks to a database or a browser. This pass is a
manual review, not a substitute for actually running
`docker compose up` and `pytest` — if you hit anything further,
share the exact error/traceback and it can be fixed directly (FIX
mode), which is far more reliable than continued manual inspection.
