"""
Embedding generation, used for semantic skill normalization and for
career/job/course similarity search over pgvector columns.

Loads the model lazily (first call only) so `uvicorn --reload` and
tests that never touch AI features don't pay the startup cost.
sentence-transformers may not be installed/downloaded in every
environment (e.g. offline CI), so we fail soft: if the model can't
load, callers get None back and should fall back to keyword-only
matching rather than crash.
"""
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dim, matches EMBEDDING_DIM in models


@lru_cache
def _get_model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(MODEL_NAME)
    except Exception as exc:  # noqa: BLE001 — deliberately broad; this is a soft-fail path
        logger.warning("Embedding model unavailable, falling back to keyword-only matching: %s", exc)
        return None


def embed_text(text: str) -> list[float] | None:
    model = _get_model()
    if model is None:
        return None
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_batch(texts: list[str]) -> list[list[float]] | None:
    model = _get_model()
    if model is None:
        return None
    return [vec.tolist() for vec in model.encode(texts, normalize_embeddings=True)]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot  # vectors are already normalized, so dot product == cosine similarity
