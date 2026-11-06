"""Retrieval: hybrid search, then semantic re-ranking.

The half that decides whether the system works - if the right passage is not in
what we hand the model, no prompt recovers it.

Stage 1 is cheap and wide: one request fusing BM25 and vector similarity, 50
candidates. Keyword wins on quoted terms, vectors win on paraphrase, and each
fails where the other works. Stage 2 is expensive and narrow: the semantic
ranker reads question and passage *together* (BM25 and cosine never do) and we
keep 5. Wide cheap net, then real compute only on the shortlist.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from rag_core import SEMANTIC_CONFIG

from .settings import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Passage:
    """One retrieved passage, carrying everything needed to cite it."""

    chunk_id: str
    doc_id: str
    doc_title: str
    section: str
    content: str
    source_url: str
    search_score: float
    reranker_score: float | None = None


def retrieve(
    question: str,
    *,
    candidate_k: int | None = None,
    final_k: int | None = None,
    use_reranker: bool = True,
) -> list[Passage]:
    """Return the passages to ground the answer in.

    use_reranker is a parameter, not a constant: the headline experiment is this
    flag flipped with everything else held constant. Built in from the start, the
    comparison is free; bolted on later, both arms get re-run by hand.

    TODO Sun AM:
      1. embed the question with the same deployment used at ingestion time
         (a different embedding model means a meaningless vector search)
      2. one search_client().search() call with:
           search_text=question                 -> BM25
           vector_queries=[VectorizedQuery(...)] -> vector, fields="content_vector"
           top=candidate_k
           query_type="semantic" if use_reranker else "simple"
           semantic_configuration_name=SEMANTIC_CONFIG
      3. read @search.score and @search.reranker_score off each result
      4. truncate to final_k and map into Passage
    """
    settings = get_settings()
    candidate_k = candidate_k or settings.candidate_k
    final_k = final_k or settings.final_k
    logger.debug(
        "retrieving: candidate_k=%d final_k=%d reranker=%s config=%s",
        candidate_k,
        final_k,
        use_reranker,
        SEMANTIC_CONFIG,
    )
    raise NotImplementedError("Sunday AM: hybrid query + semantic rerank.")


def format_passages(passages: list[Passage]) -> str:
    """Render passages for the prompt, numbered so the model can cite them.

    The numbering IS the citation contract: [2] means passages[1]. answer.py
    depends on it, so changing this format means changing the parser too.
    """
    blocks = []
    for i, passage in enumerate(passages, start=1):
        header = f"[{i}] {passage.doc_title}"
        if passage.section:
            header += f" - {passage.section}"
        blocks.append(f"{header}\n{passage.content}")
    return "\n\n---\n\n".join(blocks)
