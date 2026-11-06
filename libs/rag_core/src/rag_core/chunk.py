"""Splitting documents into retrievable pieces.

Heading-aware: a chunk never spans two sections, because "this exemption does
not apply" is meaningless without the heading above it. Within a section,
paragraphs are packed to a token budget with overlap, so a fact on a boundary
is not cut in half. See docs/architecture.md for why this is not an indexer.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


@dataclass(frozen=True)
class Chunk:
    """One retrievable passage. chunk_id is deterministic, so re-ingesting
    unchanged input keeps citations valid and runs comparable."""

    chunk_id: str
    doc_id: str
    doc_title: str
    section: str
    ordinal: int
    text: str
    source_url: str = ""
    page: int | None = None
    metadata: dict[str, str] = field(default_factory=dict)


def estimate_tokens(text: str) -> int:
    """~4 characters per token. Swap in tiktoken if you start tuning chunk
    sizes hard, but not before."""
    return max(1, len(text) // 4)


def split_sections(markdown: str) -> list[tuple[str, str]]:
    """Split on markdown headings into (section_title, body) pairs.

    Text before the first heading is returned under the section "".
    """
    matches = list(HEADING_RE.finditer(markdown))
    if not matches:
        return [("", markdown.strip())]

    sections: list[tuple[str, str]] = []
    preamble = markdown[: matches[0].start()].strip()
    if preamble:
        sections.append(("", preamble))

    for i, match in enumerate(matches):
        title = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        if body:
            sections.append((title, body))

    return sections


def _pack_paragraphs(paragraphs: list[str], target_tokens: int, overlap_ratio: float) -> list[str]:
    """Greedily pack paragraphs into chunks, carrying overlap between them."""
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = estimate_tokens(para)

        if current and current_tokens + para_tokens > target_tokens:
            chunks.append("\n\n".join(current))
            # Carry the tail forward so a fact on the boundary appears whole once.
            overlap_budget = int(target_tokens * overlap_ratio)
            carried: list[str] = []
            carried_tokens = 0
            for prev in reversed(current):
                prev_tokens = estimate_tokens(prev)
                if carried_tokens + prev_tokens > overlap_budget:
                    break
                carried.insert(0, prev)
                carried_tokens += prev_tokens
            current = carried
            current_tokens = carried_tokens

        current.append(para)
        current_tokens += para_tokens

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def chunk_document(
    *,
    doc_id: str,
    doc_title: str,
    markdown: str,
    source_url: str = "",
    target_tokens: int = 700,
    overlap_ratio: float = 0.15,
) -> list[Chunk]:
    """Split one document into Chunks. Pure function - no I/O, easy to test."""
    chunks: list[Chunk] = []
    ordinal = 0

    for section_title, body in split_sections(markdown):
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        if not paragraphs:
            continue

        for text in _pack_paragraphs(paragraphs, target_tokens, overlap_ratio):
            # Prepended: strong retrieval signal, cheap to carry.
            prefixed = f"{section_title}\n\n{text}" if section_title else text
            digest = hashlib.sha256(f"{doc_id}|{section_title}|{ordinal}".encode()).hexdigest()[:16]

            chunks.append(
                Chunk(
                    chunk_id=digest,
                    doc_id=doc_id,
                    doc_title=doc_title,
                    section=section_title,
                    ordinal=ordinal,
                    text=prefixed,
                    source_url=source_url,
                )
            )
            ordinal += 1

    return chunks
