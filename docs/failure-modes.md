# Failure modes

Six deliberate breakages, each with everything else held constant. This is the
part of the project that is actually interesting: anyone can show a RAG app
answering three questions they picked.

Fill the table from real runs. Leave a row blank rather than guessing — a table
of invented numbers is worse than no table.

| # | Change | Expected effect | recall@5 | grounded | abstention | What actually happened |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Semantic re-ranker off** (hybrid only) | fewer right passages in top 5 | | | | |
| 2 | **Chunk size 200 tokens** (from 700) | passages lose their context | | | | |
| 3 | **Chunk size 1500 tokens** | answer buried in irrelevant text | | | | |
| 4 | **`candidate_k = 5`** (from 50) | re-ranker has nothing to work with | | | | |
| 5 | **Contradictory documents** added | should cite both and say they disagree | | | | |
| 6 | **Answer inside a table** | extraction loses the structure | | | | |

Reproduce any row with:

```bash
python eval/run_eval.py --live --no-reranker          # row 1
# rows 2-4: change settings.py, re-ingest, re-run
```

## Notes to write up as you go

**Row 1** is the headline experiment and the one quoted in the README. Run it
three times per arm — the difference between arms must be larger than the spread
within an arm to mean anything.

**Rows 2 and 3** are the same knob in both directions, and that is the point:
chunk size has an interior optimum, not a monotonic effect. Being able to say
where yours sits, and why, is more convincing than any number.

**Row 4** isolates the two-stage retrieval argument. If `candidate_k = 5`
performs as well as 50, the re-ranker is not earning its latency on this corpus
and you should say so rather than keep it for appearances.

**Row 5** needs documents built by hand. Worth the effort: real corpora contradict
themselves constantly — superseded policies, regional variants — and silently
picking one source is the failure users never notice.

**Row 6** will probably just fail, and that is a legitimate finding. Record which
extraction step loses the structure and what fixing it would take.

## Failures found outside the matrix

Keep a running list as you build. Unplanned findings are often the best
interview material.

- _(e.g. near-duplicate sections across two documents: the ranker preferred the
  stale one because its heading matched the question more literally)_
