"""Is every claim supported by the retrieved passages?

Judged by a model, so: the judge is stronger than the generator (grading its
own output measures confidence, not accuracy), and a sample of verdicts is
hand-checked with the agreement rate reported. Without that rate, "94%
grounded" could be a good system or a lenient judge and no reader can tell.

Reported as the share of answers with zero unsupported claims rather than an
average, because one fabricated sentence makes an answer unusable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Verdict(StrEnum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"  # passages are silent on this claim
    CONTRADICTED = "contradicted"  # passages say otherwise - the worst case


@dataclass(frozen=True)
class ClaimVerdict:
    claim: str
    verdict: Verdict
    reasoning: str = ""


@dataclass(frozen=True)
class GroundednessResult:
    question_id: str
    claims: list[ClaimVerdict]

    @property
    def fully_grounded(self) -> bool:
        return all(c.verdict is Verdict.SUPPORTED for c in self.claims)

    @property
    def unsupported_count(self) -> int:
        return sum(1 for c in self.claims if c.verdict is not Verdict.SUPPORTED)


def score_one(*, question_id: str, answer: str, passages: list[str], judge) -> GroundednessResult:
    """TODO Sun PM: split the answer into atomic claims, judge each against the
    passages with eval/judge_prompts/groundedness.md, and require structured
    output - parsing "well, arguably supported..." is how harnesses rot.
    """
    raise NotImplementedError("Sunday PM: claim-level groundedness judging.")


def share_fully_grounded(results: list[GroundednessResult]) -> float:
    """The headline number. Share of answers with no unsupported claims."""
    if not results:
        return 0.0
    return sum(1 for r in results if r.fully_grounded) / len(results)
