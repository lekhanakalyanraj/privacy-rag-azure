"""Generation: prompt, citation contract, abstention.

Three prompt rules, each matching a metric: answer only from the passages
(groundedness), cite every factual sentence (citation validity), and emit the
sentinel below when the passages fall short (correct abstention).

The sentinel is an exact string rather than "I don't know" so detection is a
comparison, not fuzzy matching on prose. A metric that depends on the model's
wording drifts as the model changes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

ABSTAIN_SENTINEL = "NOT_IN_PROVIDED_DOCUMENTS"

CITATION_RE = re.compile(r"\[(\d+)\]")

SYSTEM_PROMPT = f"""You answer questions using ONLY the numbered passages provided.

Rules:
1. Every factual sentence must end with a citation naming the passage it came \
from, like [1] or [2][3]. Never cite a passage number that was not provided.
2. Never use knowledge from outside the passages, even if you are confident it \
is correct.
3. If the passages do not contain enough information to answer, reply with \
exactly this and nothing else: {ABSTAIN_SENTINEL}
4. If the passages disagree with each other, say so explicitly and cite both.
5. Be concise. Do not restate the question or pad the answer.
"""

USER_PROMPT = """Passages:

{passages}

Question: {question}"""


@dataclass(frozen=True)
class Answer:
    text: str
    cited_passages: list[int]
    abstained: bool
    prompt_tokens: int = 0
    completion_tokens: int = 0


def build_messages(question: str, formatted_passages: str) -> list[dict[str, str]]:
    """Assemble the chat messages. Pure, so it is trivially testable."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_PROMPT.format(passages=formatted_passages, question=question),
        },
    ]


def parse_citations(text: str) -> list[int]:
    """Extract cited passage numbers, de-duplicated, in order of first use."""
    seen: dict[int, None] = {}
    for match in CITATION_RE.finditer(text):
        seen.setdefault(int(match.group(1)), None)
    return list(seen)


def invalid_citations(text: str, n_passages: int) -> list[int]:
    """Citations pointing at passages that were never supplied.

    The cheap half of citation validity, and it needs no model: a [7] when only
    5 passages were given is simply wrong. Whether passage 2 actually *supports*
    the sentence is the expensive half, in eval/metrics/citations.py.
    """
    return [n for n in parse_citations(text) if n < 1 or n > n_passages]


def is_abstention(text: str) -> bool:
    return text.strip() == ABSTAIN_SENTINEL


def generate(question: str, formatted_passages: str, n_passages: int) -> Answer:
    """Call the chat deployment and wrap the result.

    TODO Sun AM:
      1. clients.openai_client().chat.completions.create(
             model=settings.chat_deployment,
             messages=build_messages(...),
             temperature=settings.temperature,   # 0.0 - this is a reading task
             max_tokens=settings.max_answer_tokens)
      2. populate Answer, including token usage so cost per question is visible
      3. log any invalid_citations() rather than silently dropping them - a
         model inventing passage numbers is a signal, not noise
    """
    raise NotImplementedError("Sunday AM: chat completion.")
