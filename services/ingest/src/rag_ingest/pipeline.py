"""Orchestration: documents in, search index out.

Idempotent - same input, same chunk_ids, so re-running keeps citations valid
and runs comparable. See docs/architecture.md for why this is a job.
"""

from __future__ import annotations

import logging
from pathlib import Path

from rag_core import build_index, chunk_document
from rag_core.chunk import Chunk

from . import sources
from .clients import index_admin_client
from .embed import embed_texts
from .settings import get_settings

logger = logging.getLogger(__name__)


def chunk_all(documents: list[sources.SourceDocument]) -> list[Chunk]:
    """Chunk every document with the configured settings."""
    settings = get_settings()
    chunks: list[Chunk] = []

    for document in documents:
        chunks.extend(
            chunk_document(
                doc_id=document.doc_id,
                doc_title=document.title,
                markdown=document.text,
                source_url=document.source_url,
                target_tokens=settings.chunk_target_tokens,
                overlap_ratio=settings.chunk_overlap_ratio,
            )
        )

    logger.info("%d documents -> %d chunks", len(documents), len(chunks))
    return chunks


def to_search_documents(chunks: list[Chunk], vectors: list[list[float]]) -> list[dict]:
    """Map chunks and their embeddings onto the index schema.

    strict=True is deliberate: a length mismatch would upload documents with
    the wrong vectors, giving an index that looks fine and retrieves nonsense.
    """
    return [
        {
            "chunk_id": chunk.chunk_id,
            "doc_id": chunk.doc_id,
            "doc_title": chunk.doc_title,
            "section": chunk.section,
            "content": chunk.text,
            "source_url": chunk.source_url,
            "ordinal": chunk.ordinal,
            "content_vector": vector,
        }
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]


def ensure_index(*, recreate: bool) -> None:
    """Create the index, optionally rebuilding it from scratch."""
    settings = get_settings()
    index = build_index(settings.search_index_name, settings.embedding_dimensions)
    logger.info("index %s: %d fields, recreate=%s", index.name, len(index.fields or []), recreate)
    raise NotImplementedError(
        f"Saturday PM: {index_admin_client.__name__}().create_or_update_index(index), "
        f"deleting {index.name} first when recreate is set. Changing a field type or "
        "the vector dimensionality requires a rebuild - Azure will not do it in place."
    )


def run(*, local_path: Path | None = None, recreate: bool = False) -> None:
    """The whole pipeline. Called by __main__ and by the Container Apps Job."""
    documents = sources.from_local(local_path) if local_path else sources.from_blob()
    chunks = chunk_all(documents)
    vectors = embed_texts([chunk.text for chunk in chunks])

    ensure_index(recreate=recreate)
    documents_to_upload = to_search_documents(chunks, vectors)

    logger.info("uploading %d documents", len(documents_to_upload))
    raise NotImplementedError(
        "Saturday PM: upload in batches of settings.upload_batch_size via "
        "rag_core.clients.search_client().upload_documents()."
    )
