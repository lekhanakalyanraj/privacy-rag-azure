"""Embedding, with an on-disk cache keyed on (model, dimensions, text).

Re-running ingestion after a chunking tweak only pays for chunks that changed -
the difference between a 10-second loop and a 3-minute one. Cached under
.cache/, which is gitignored: regenerable and large.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from .settings import get_settings

logger = logging.getLogger(__name__)

CACHE_DIR = Path(".cache/embeddings")


def cache_key(text: str, model: str, dimensions: int) -> str:
    """Dimensions are in the key: the same text at 512 and 1536 are different
    vectors, and mixing them in one index fails silently."""
    return hashlib.sha256(f"{model}|{dimensions}|{text}".encode()).hexdigest()


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def read_cached(key: str) -> list[float] | None:
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        # Not worth crashing over - re-embed it.
        logger.warning("discarding unreadable cache entry %s", key[:12])
        return None


def write_cached(key: str, vector: list[float]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(key).write_text(json.dumps(vector))


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed every text, using the cache where possible.

    TODO Sat PM:
      1. read_cached() each key
      2. batch the misses in groups of settings.embed_batch_size through
         openai_client().embeddings.create(model=..., input=batch,
         dimensions=settings.embedding_dimensions)
      3. write_cached() before returning, so an interrupted run keeps what it
         already paid for
      4. preserve input order - the caller zips against chunks, so a reordering
         corrupts the index silently
    """
    settings = get_settings()
    keys = [
        cache_key(text, settings.embedding_deployment, settings.embedding_dimensions)
        for text in texts
    ]
    hits = sum(1 for key in keys if read_cached(key) is not None)
    logger.info("embedding %d texts (%d cached, %d to fetch)", len(texts), hits, len(texts) - hits)

    raise NotImplementedError("Saturday PM: batch the cache misses through the embeddings API.")
