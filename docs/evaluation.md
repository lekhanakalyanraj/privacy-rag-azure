# Evaluation

## Why four metrics and not one

A RAG system fails in distinguishable ways, and a single score hides which one
is happening. Each metric below isolates one failure.

| Metric | Question it answers | Needs a model? | Where |
| --- | --- | --- | --- |
| Retrieval recall@5 | Did the right passage reach the prompt? | No | `eval/metrics/retrieval.py` |
| Citation resolvable | Does `[2]` point at a supplied passage? | No | `eval/metrics/citations.py` |
| Citation supported | Does passage 2 actually support that sentence? | Yes | `eval/metrics/citations.py` |
| Groundedness | Is every claim backed by the passages? | Yes | `eval/metrics/groundedness.py` |
| Correct abstention | Does it refuse when the corpus cannot answer? | No | `eval/metrics/abstention.py` |

Read them in that order when a run looks bad. If recall@5 is low, nothing
downstream can help and the prompt is not the problem.

The two citation checks are reported separately on purpose. A system can score
100% resolvable and 60% supported — answers that look sourced and are not. That
gap is usually the most informative number in a report.

## The golden set

60 questions in `eval/golden/questions.yaml`: 50 answerable, each tagged with
the chapter and section that answers it, and **10 deliberately unanswerable** —
plausible, on-topic, genuinely absent from the corpus. Penalties, case law and
the text of the Privacy Act itself all sit outside the guidelines, so there is
no shortage of material for those ten.

The 10 matter more than their share suggests. A model that answers them is
drawing on pre-training rather than the corpus, which is the exact behaviour
that makes a grounded-answer system untrustworthy, and you only detect it by
testing for it.

**Validate each one before trusting it:** ask the question with no context at
all. If the model answers correctly from memory, that question is contaminated
and measures nothing — replace it. Privacy law is partly memorised, so this
check is not optional for this corpus.

Written *before* any tuning. A golden set assembled after seeing the failures is
a golden set shaped around them.

Matching is on `(doc_id, section)`, never `chunk_id`: re-chunking the corpus
changes every chunk id, which would silently invalidate the whole set. `doc_id`
is the chapter filename stem, so renaming a fetched file breaks it too.

## The judge, and who judges the judge

Groundedness and citation support need judgement, so a model provides it.
Two safeguards:

1. **The judge is stronger than the generator** (`gpt-4.1` judging
   `gpt-4.1-mini`). A model grading its own output measures its confidence, not
   its accuracy.
2. **A 20% sample of verdicts is hand-checked and the agreement rate reported.**
   Without that number, "94% grounded" is uninterpretable — it could be a good
   system or a lenient judge, and no reader can tell which.

Judge prompts are committed in `eval/judge_prompts/`. A prompt that lives only
in a shell history makes every number it produced unreproducible.

## Live vs replay

| | `--live` | `--replay` |
| --- | --- | --- |
| Calls Azure | yes | no |
| Costs | ~A$0.20/run | nothing |
| Deterministic | no | yes |
| Runs | nightly + on demand | every pull request |

Replay re-scores recorded responses, so changes to the *metric code* are tested
without a cloud round-trip. Both modes share one scoring path — if they
diverged, replay would be theatre.

## The gate

`--gate eval/baselines/<date>.json` compares the run to a committed baseline and
exits non-zero if a metric drops past the tolerance in `eval/run_eval.py`.

Tolerances are not zero. These numbers move between runs even at temperature 0,
because retrieval ties and judge calls are not perfectly stable. Set each
tolerance from the spread observed across three real runs: tighter than the
noise floor produces failures nobody believes, and a gate nobody believes gets
switched off.

## Quoting a number honestly

- Three runs minimum; report mean and range.
- If a difference is smaller than the run-to-run spread, there is no result yet.
  Say that instead of rounding in your own favour.
- Always state n, the corpus size, both model names, and the judge agreement rate.
