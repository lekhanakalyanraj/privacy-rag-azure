"""Does it refuse when the corpus cannot answer?

Deterministic: the prompt specifies an exact sentinel, so this is a comparison
rather than a judgement about tone. Imported from rag_api rather than
redefined - a metric holding its own copy of the contract stops measuring it.

The two error directions are not symmetric: answering something absent is
dangerous, refusing something present is annoying. Reported separately, because
a system that abstains on everything scores perfectly on the first.
"""

from __future__ import annotations

from dataclasses import dataclass

from rag_api.answer import is_abstention


@dataclass(frozen=True)
class AbstentionResult:
    question_id: str
    answerable: bool
    abstained: bool

    @property
    def correct(self) -> bool:
        return self.abstained != self.answerable


def score_one(*, question_id: str, answerable: bool, answer: str) -> AbstentionResult:
    return AbstentionResult(
        question_id=question_id,
        answerable=answerable,
        abstained=is_abstention(answer),
    )


def correct_abstention_rate(results: list[AbstentionResult]) -> float:
    """Of the unanswerable questions, how many were correctly refused?"""
    unanswerable = [r for r in results if not r.answerable]
    if not unanswerable:
        return 0.0
    return sum(1 for r in unanswerable if r.abstained) / len(unanswerable)


def over_abstention_rate(results: list[AbstentionResult]) -> float:
    """Of the answerable questions, how many were wrongly refused?"""
    answerable = [r for r in results if r.answerable]
    if not answerable:
        return 0.0
    return sum(1 for r in answerable if r.abstained) / len(answerable)
