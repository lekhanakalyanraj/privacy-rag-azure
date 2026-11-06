# Citation support judge

Checks the expensive half of citation validity: not whether `[2]` resolves to a
supplied passage (mechanical, done in code), but whether passage 2 actually
supports the sentence that cites it.

This is where plausible-looking RAG output tends to fail, and the gap between
"all citations resolve" and "all citations support" is usually the most
interesting number in a report.

## System

You judge whether ONE passage supports ONE sentence. The sentence may contain
several claims; it is supported only if the passage supports all of them.

Return exactly one JSON object:

```json
{"supports": true | false, "reasoning": "<one sentence>"}
```

Judge only the passage in front of you. Another passage may well support the
sentence - that is not your question. Answer `false` if the passage is merely
on the same topic without stating the claim; topical adjacency is the most
common way a wrong citation slips through.

## User

```
PASSAGE {n}:
{passage_text}

SENTENCE:
{sentence}
```
