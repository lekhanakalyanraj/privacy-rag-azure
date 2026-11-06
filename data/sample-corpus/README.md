# Corpus

Put 20–40 markdown or text documents here, then `make ingest`.

Deliberately empty: the corpus is a real choice, not boilerplate, and a fake one
left in the repo tends to get mistaken for the real one.

## What to pick

**One coherent domain**, not a big pile. Coherence beats volume, because the
interesting questions are the ones where two sections nearly answer and only one
actually does. A grab-bag of unrelated documents makes retrieval trivially easy
and the evaluation meaningless.

Needs to satisfy:

- **Real answers.** You must be able to point at the section answering each
  golden question.
- **Real near-misses.** Sections that look relevant and are not. This is where
  re-ranking earns its place.
- **Genuine absences.** Things a user would plausibly ask that the corpus simply
  does not cover — these become the 10 unanswerable questions.
- **Public and quotable**, so the repo can stay public.

Candidates that work well: the Australian Privacy Principles plus OAIC
guidance; ASIC regulatory guides; the documentation for a single open-source
project.

## Constraints

- Free tier is **50 MB total**, which is roughly 400–800 chunks. Comfortable.
  A few thousand is not.
- Markdown and plain text only to start with. PDFs need an extraction step and
  tables will lose their structure — that is failure-mode row 6, worth hitting
  deliberately rather than by accident on day one.
- Keep filenames stable. The filename stem becomes `doc_id`, which the golden
  set references; renaming a file silently invalidates those questions.
