# Onboarding

For someone who has never worked on a RAG system or on Azure. No prior
knowledge assumed.

## The problem

A language model knows a lot, but it does not know *your* documents. Ask it a
question about a specific regulation and it produces something confident and
plausible that may be subtly wrong, with no way to check it.

The fix is unglamorous: **don't ask the model to remember, give it the relevant
text and ask it to read.** Find the handful of paragraphs that answer the
question, put them in the prompt, and require the model to answer only from
those and to say where each claim came from. That is retrieval-augmented
generation — retrieval (find the right paragraphs) augmenting generation (write
the answer).

So there are two halves, and almost all the difficulty is in the first. If
retrieval hands over the wrong paragraphs, no amount of prompt tuning recovers
it. The beginner's instinct is to spend the time on the prompt; the real work is
in retrieval and in knowing when it failed.

## Setup, which happens once

1. Documents sit in **Blob Storage** — a folder in the cloud. Nothing clever.
2. A script splits each document into chunks of roughly a page. Why split? You
   cannot fit a whole regulation into a prompt, and even if you could, burying
   the answer in 200 pages makes the model worse at finding it. Smaller chunks
   mean sharper retrieval — but too small and a chunk loses the context that
   gives it meaning: "this does not apply" is useless without the sentence
   above it. That balance is measured, not guessed (`docs/failure-modes.md`).
3. Each chunk becomes an **embedding** — ~1500 numbers encoding roughly what the
   text means. Similar meaning, similar numbers. This is what allows searching
   by meaning rather than by exact words.
4. Chunks, embeddings and metadata go into **Azure AI Search**, a database built
   for exactly this kind of lookup.

## A question, end to end

1. **Embed the question** the same way the chunks were embedded.
2. **Search two ways at once.** Keyword search finds literal word matches —
   right when the user quotes an exact term. Vector search finds similar
   meaning — right when they paraphrase. Each fails where the other works, so
   both run and the rankings are merged. That is **hybrid search**. We ask for
   50 candidates, deliberately over-fetching.
3. **Re-rank.** Those 50 are ordered by two crude scores that never actually
   read the question and the passage *together*. So they go to a second, smarter
   model — Azure's **semantic ranker** — which does, and reorders them properly.
   Keep the top 5. It is expensive per item, which is why it only sees 50
   candidates rather than the whole index. Cheap wide net, then expensive
   shortlist: the most transferable idea in this project.
4. **Generate.** The 5 passages go into the prompt, numbered, with instructions:
   answer only from these, put a `[2]` on every factual sentence, and if the
   answer is not there, say so rather than guess.
5. **Return the receipts** — the answer, the citations, and what was retrieved —
   so a human and the test suite can both check whether a citation actually
   supports the sentence attached to it.

Two words used constantly: an answer is **grounded** if every claim traces back
to retrieved text, and **abstention** is correctly saying "not covered here".
Abstention is a feature. A system that answers everything is a system that lies
sometimes.

## Why there is a test harness, and what is unusual about it

Normal tests assert that output equals 4. This is not that — there is no single
correct string for a question, and the same question can produce different text
on two runs. So we test the properties that matter, on 60 hand-written
questions (the **golden set**):

- **Did retrieval find the right section?** We know which document answers each
  question, so this is pass/fail and needs no AI at all. The most trustworthy
  number in the harness.
- **Does every citation hold up?** Two separate checks, often conflated. Does
  `[2]` point at a passage we supplied — mechanical. Does that passage
  *genuinely support* the sentence — needs judgement. The second is where RAG
  quietly fails: confident answers with real-looking citations that do not say
  what the answer claims.
- **Is anything unsupported?** The same idea over the whole answer.
- **Does it refuse when it should?** Ten questions are deliberately
  unanswerable. A system that invents answers for those is dangerous, and you
  only find out by testing on purpose.

The judgement calls use another model as a grader — which raises the obvious
problem of who grades the grader. Two safeguards: the judge is a *stronger*
model than the one writing answers, and we hand-check 20% of its verdicts and
report how often we agreed. That number is what makes the evaluation believable
rather than circular. If you take one habit from this project, take that one.

The baseline numbers are committed, and the pipeline re-runs everything nightly
and **fails the build if quality drops**. That is the actual point. Anyone can
demo a RAG app that works on the three questions they tried.

## The infrastructure half

All of this has to live somewhere. You could click through the Azure portal for
an afternoon and it would work — and then you would have no record of what you
did, no way to rebuild it, and no way to show anyone. Six weeks later nobody
remembers which checkbox mattered.

**Terraform** is how you write the cloud down. Describe the resources in files,
run `terraform apply`, and it makes reality match. Change a file, apply again,
it adjusts the difference. `terraform destroy` removes everything. It keeps a
**state file** — its ledger of what it created, so it knows "make this new" from
"change this existing thing".

Which gives the most convincing demo in the repo: **destroy everything, apply
again, re-ingest, re-run the eval, get the same numbers.** That cannot be faked.

**GitHub Actions** is the robot that runs on every change: lint and test on a
pull request, show the Terraform plan as a comment so you see what *would*
change before it does, deploy on merge, run the full evaluation nightly.

Two security ideas worth internalising, because they come up in interviews:

- **Managed identity** — the app has no password. Azure vouches for it directly:
  "this container may read that search index." No key to leak, rotate or
  accidentally commit. That is what `DefaultAzureCredential` is doing in
  `clients.py`.
- **OIDC** — the same idea for the pipeline. Instead of storing an Azure
  password in GitHub, GitHub hands Azure a short-lived signed token saying "I am
  genuinely the main branch of this repo". Nothing long-lived exists to steal.

The instinct behind both: a secret you never stored cannot leak.

## Why it costs nothing

Search runs on a free shared tier. The model charges per token and 60 questions
is cents. The container **scales to zero** — idle means nothing running and
nothing billed, at the cost of a slow first request, which is a fine trade here.
Images live in GitHub's registry because Azure's has no free tier.

The free tier shapes one visible design choice, worth understanding rather than
treating as a hack: Azure Search can ingest documents for you, but on the free
tier only 20 a day. So chunking and embedding happen in Python — which is *more*
defensible anyway, because we can explain and tune our chunking where the
built-in path is a black box.

## Where to start reading

`app/src/rag/__init__.py` lists the modules in the order data flows through
them. Then `docs/architecture.md` for the decisions, and
`docs/failure-modes.md` for what breaks.
