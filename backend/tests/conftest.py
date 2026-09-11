"""
Shared test fixtures. Uses an isolated in-memory SQLite database for
speed. Vector columns are excluded from SQLite runs (pgvector is
Postgres-only) — tests that exercise embedding-backed semantic
matching are marked and skipped unless POSTGRES_TEST_URL is set,
documented in each test module that needs it.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app
import app.models  # noqa: F401 populate metadata

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture()
def db_session():
    # StaticPool pins the whole engine to a single underlying
    # connection, which is required for `sqlite:///:memory:` to work
    # correctly here: FastAPI's TestClient can dispatch a request onto
    # a different thread than the one that created the fixture, and
    # SQLite's default per-thread pooling would otherwise hand that
    # request a brand-new, empty in-memory database ("no such table").
    engine = create_engine(
        TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
