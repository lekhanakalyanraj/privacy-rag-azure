"""Do the citations hold up? Two checks that get conflated and should not be:

1. Resolvable - does [2] point at a passage we supplied? Mechanical.
2. Supported - does passage 2 contain the claim? Needs a judge.

Report them separately. 100% resolvable with 60% supported is the most useful
number in the harness: answers that look sourced and are not.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
CITATION_RE = re.compile(r"\[(\d+)\]")


@dataclass(frozen=True)
class SentenceCitation:
    sentence: str
    cited: list[int]


@dataclass(frozen=True)
class CitationResult:
    question_id: str
    sentences_total: int
    sentences_with_citations: int
    unresolvable: list[int]
    supported: int
    unsupported: int

    @property
    def resolvable_rate(self) -> float:
        return 1.0 if not self.unresolvable else 0.0

    @property
    def support_rate(self) -> float:
        judged = self.supported + self.unsupported
        return self.supported / judged if judged else 0.0


def split_cited_sentences(answer: str) -> list[SentenceCitation]:
    """Break an answer into sentences and the passages each one cites."""
    out: list[SentenceCitation] = []
    for sentence in SENTENCE_RE.split(answer.strip()):
        sentence = sentence.strip()
        if not sentence:
            continue
        cited = [int(m.group(1)) for m in CITATION_RE.finditer(sentence)]
        out.append(SentenceCitation(sentence=sentence, cited=cited))
    return out


def unresolvable_citations(answer: str, n_passages: int) -> list[int]:
    """Cited passage numbers that were never supplied. No model needed."""
    cited = {int(m.group(1)) for m in CITATION_RE.finditer(answer)}
    return sorted(n for n in cited if n < 1 or n > n_passages)


def score_one(
    *,
    question_id: str,
    answer: str,
    passages: list[str],
    judge,
) -> CitationResult:
    """Score citations for one answer.

    `judge` is injected so tests can pass a stub and models can be swapped
    without touching this file.

    TODO Sun PM: one judge call per (sentence, citation) pair. Batching is
    cheaper but lets the judge smear one verdict across several claims - start
    honest, optimise if the bill justifies it.
    """
    sentences = split_cited_sentences(answer)
    cited = sum(1 for s in sentences if s.cited)
    raise NotImplementedError(
        f"Sunday PM: judge {cited} of {len(sentences)} sentences against their "
        f"cited passages using eval/judge_prompts/citation_support.md "
        f"(judge={judge!r}, question={question_id}, passages={len(passages)})."
    )
