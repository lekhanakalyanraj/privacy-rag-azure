"""Reading the source corpus: local disk for development and tests, blob
storage for the deployed job. Keeping both means chunking can be tuned without
a cloud round-trip.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

TEXT_SUFFIXES = {".md", ".txt"}


@dataclass(frozen=True)
class SourceDocument:
    """One document before chunking. doc_id is what the golden set references,
    so renaming a file silently invalidates every question pointing at it."""

    doc_id: str
    title: str
    text: str
    source_url: str = ""


def _title_from_text(text: str, fallback: str) -> str:
    """First markdown heading, or the filename."""
    first_line = text.lstrip().split("\n", 1)[0]
    return first_line.lstrip("# ").strip() or fallback


def from_local(root: Path) -> list[SourceDocument]:
    """Read every markdown or text file under root."""
    documents: list[SourceDocument] = []

    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        documents.append(
            SourceDocument(
                doc_id=path.stem,
                title=_title_from_text(text, path.stem),
                text=text,
                source_url=str(path),
            )
        )

    logger.info("read %d documents from %s", len(documents), root)
    return documents


def from_blob() -> list[SourceDocument]:
    """Read the corpus container.

    TODO Sat PM:
      1. blob_client().get_container_client(settings.blob_container)
      2. list_blobs(), skipping anything not in TEXT_SUFFIXES
      3. download and decode as UTF-8
      4. doc_id = blob name minus extension, matching from_local()

    PDFs need extraction first; add it once the pipeline works end to end. A
    half-working extractor makes every downstream number untrustworthy.
    """
    raise NotImplementedError("Saturday PM: read the corpus from blob storage.")
