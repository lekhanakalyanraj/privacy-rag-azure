"""Ingestion-only configuration: where the corpus is and how it is cut up."""

from functools import lru_cache

from rag_core.settings import CoreSettings


class IngestSettings(CoreSettings):
    # --- Source corpus ---
    blob_endpoint: str = ""
    blob_container: str = "corpus"

    # --- Chunking ---
    # Highest-leverage numbers here - see docs/failure-modes.md rows 2 and 3.
    chunk_target_tokens: int = 700
    chunk_overlap_ratio: float = 0.15

    # --- Throughput ---
    embed_batch_size: int = 64
    upload_batch_size: int = 500


@lru_cache
def get_settings() -> IngestSettings:
    return IngestSettings()  # type: ignore[call-arg]
