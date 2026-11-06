"""API-only configuration: retrieval shape and generation parameters."""

from functools import lru_cache

from rag_core.settings import CoreSettings


class ApiSettings(CoreSettings):
    chat_deployment: str = "gpt-4-1-mini"

    # Over-fetch cheaply, re-rank expensively. The main lever on retrieval
    # quality - see docs/failure-modes.md rows 1 and 4.
    candidate_k: int = 50
    final_k: int = 5

    # Zero: this is a reading task, not a writing task.
    temperature: float = 0.0
    max_answer_tokens: int = 800


@lru_cache
def get_settings() -> ApiSettings:
    return ApiSettings()  # type: ignore[call-arg]
