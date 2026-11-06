# Corpus

The **Australian Privacy Principles guidelines**, published by the OAIC.

```bash
python scripts/fetch_corpus.py          # the 10 [CORE] chapters
python scripts/fetch_corpus.py --all    # all 18
```

Licence and required attribution: [ATTRIBUTION.md](ATTRIBUTION.md). The chapter
text is fetched, not committed — see that file for why.

## Why this corpus

- **Real near-misses.** Each APP gets a chapter with near-identical headings
  ("What does APP 7 say?", "What does APP 8 say?"). Several chapters discuss
  consent, reasonable expectations and permitted situations in slightly
  different terms. That is precisely where keyword search picks the wrong
  section and the semantic re-ranker has to earn its place.
- **Real multi-hop questions.** Use and disclosure (APP 6) and direct marketing
  (APP 7) interact; permitted general situations (Chapter C) qualifies several
  others. Answering properly needs two chapters, not one.
- **Genuine absences.** Penalties, case law and the Act's own text are outside
  the guidelines, so plausible on-topic questions have no answer in the corpus —
  which is what the 10 unanswerable golden questions are built from.
- **Only partly memorised.** The model knows the APPs exist and roughly what
  they cover, but not the guidance wording. That matters: a corpus the model
  knows well makes groundedness and abstention unmeasurable, because it can
  answer the unanswerable questions correctly from memory.

## Measured size

Mean ~47,000 characters per chapter. All 18 come to roughly 300 chunks and
1.8 MB of vectors at 1536 dimensions, well inside the Free tier's 50 MB. Storage
is not the constraint here; iteration speed is, which is why `[CORE]` exists.

## Constraints to keep

- `doc_id` is the filename stem, and the golden set references it. **Renaming a
  file silently invalidates every question pointing at it.**
- The fetcher keeps headings verbatim, including long ones. Golden-set
  `gold_section` values must match the fetched text exactly.
- HTML only. The OAIC also publishes PDFs; those lose table structure, which is
  failure-mode row 6 — worth hitting deliberately, later, not on day one.

## Not legal advice

A retrieval and evaluation exercise. The assistant answers from the guidance and
cites it; it is not a compliance tool.
