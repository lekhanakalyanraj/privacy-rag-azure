"""Shared by the API service and the ingestion job.

    settings.py       configuration common to both
    clients.py        credential and read-side client construction
    chunk.py          the chunking algorithm
    index_schema.py   the index definition - the contract between the two

Only things that would break *both* deployables belong here. Retrieval and
generation are API-only; blob reading and the embedding cache are ingestion-only.
"""

from .chunk import Chunk, chunk_document
from .index_schema import SEMANTIC_CONFIG, build_index
from .settings import CoreSettings, get_settings

__all__ = [
    "SEMANTIC_CONFIG",
    "Chunk",
    "CoreSettings",
    "build_index",
    "chunk_document",
    "get_settings",
]
__version__ = "0.1.0"
