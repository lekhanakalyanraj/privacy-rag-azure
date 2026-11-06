"""Did retrieval find the passage that answers the question?

The most trustworthy metric here - no model, no judge, no randomness. Read it
first when a run looks bad: if it is low, nothing downstream can help.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalResult:
    question_id: str
    hit: bool
    rank: int | None  # 1-based position of the gold section, None if absent


def score_one(
    *,
    question_id: str,
    retrieved: list[dict],
    gold_doc: str,
    gold_section: str | None,
) -> RetrievalResult:
    """Find the gold passage's rank in the retrieved list.

    Matches on (doc_id, section), not chunk_id: re-chunking changes every
    chunk_id and would silently invalidate the golden set.
    """
    for position, passage in enumerate(retrieved, start=1):
        if passage.get("doc_id") != gold_doc:
            continue
        if gold_section and passage.get("section") != gold_section:
            continue
        return RetrievalResult(question_id=question_id, hit=True, rank=position)

    return RetrievalResult(question_id=question_id, hit=False, rank=None)


def recall_at_k(results: list[RetrievalResult], k: int) -> float:
    """Share of questions whose gold passage made the top k."""
    if not results:
        return 0.0
    hits = sum(1 for r in results if r.hit and r.rank is not None and r.rank <= k)
    return hits / len(results)


def mean_reciprocal_rank(results: list[RetrievalResult]) -> float:
    """Rewards ranking the right passage first, not just somewhere.

    Report next to recall@5: a change that drags the right passage from rank 1
    to rank 4 moves only this one.
    """
    if not results:
        return 0.0
    return sum(1 / r.rank for r in results if r.rank) / len(results)
