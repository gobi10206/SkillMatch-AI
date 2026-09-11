"""
Cross-dialect embedding column type.

pgvector's Vector type is Postgres-only and can't be compiled by
SQLAlchemy against SQLite, which the test suite uses for speed. This
wrapper uses the real pgvector Vector type in production/Postgres and
transparently falls back to a JSON-encoded TEXT column on any other
dialect, so `Base.metadata.create_all()` works in both environments.
Similarity search in tests should go through app.ai.embeddings
helpers (pure Python), not a DB-level vector query, since the
fallback storage has no index.
"""
import json

from pgvector.sqlalchemy import Vector as PgVector
from sqlalchemy.types import TypeDecorator, Text


class PortableVector(TypeDecorator):
    impl = Text
    cache_ok = True

    def __init__(self, dim: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgVector(self.dim))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.dumps(list(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return json.loads(value)
