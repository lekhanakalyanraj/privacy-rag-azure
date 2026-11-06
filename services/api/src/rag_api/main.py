"""HTTP surface.

/ask returns the retrieval trace with the answer - chunk ids, scores, token
usage. The eval harness then needs one call, and a wrong answer can be blamed
on retrieval or on generation without guessing.
"""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI
from pydantic import BaseModel, Field

from . import answer as answer_mod
from . import retrieve as retrieve_mod
from .settings import get_settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Azure RAG assistant",
    version="0.1.0",
    description="Question answering over a document corpus, with citations.",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    # So the eval harness can run both arms against the deployed service.
    use_reranker: bool = True


class RetrievedPassage(BaseModel):
    chunk_id: str
    doc_title: str
    section: str
    search_score: float
    reranker_score: float | None = None


class AskResponse(BaseModel):
    answer: str
    abstained: bool
    cited_passages: list[int]
    retrieved: list[RetrievedPassage]
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Probe. Touches no dependency on purpose: a failing search service should
    surface as a failing request, not a container stuck in a restart loop."""
    return {"status": "ok"}


@app.get("/config")
def config() -> dict[str, object]:
    """What this revision is actually pointed at. Useful the first time a
    deploy looks fine but queries an empty index."""
    settings = get_settings()
    return {
        "index": settings.search_index_name,
        "chat_deployment": settings.chat_deployment,
        "embedding_deployment": settings.embedding_deployment,
        "candidate_k": settings.candidate_k,
        "final_k": settings.final_k,
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """TODO Sun AM: wire retrieve -> format -> generate and fill the response."""
    started = time.perf_counter()

    passages = retrieve_mod.retrieve(request.question, use_reranker=request.use_reranker)
    formatted = retrieve_mod.format_passages(passages)
    result = answer_mod.generate(request.question, formatted, len(passages))

    return AskResponse(
        answer=result.text,
        abstained=result.abstained,
        cited_passages=result.cited_passages,
        retrieved=[
            RetrievedPassage(
                chunk_id=p.chunk_id,
                doc_title=p.doc_title,
                section=p.section,
                search_score=p.search_score,
                reranker_score=p.reranker_score,
            )
            for p in passages
        ],
        latency_ms=int((time.perf_counter() - started) * 1000),
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
    )
