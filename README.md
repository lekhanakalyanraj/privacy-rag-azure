# azure-rag-foundry

Question answering over a document corpus on Microsoft Foundry and Azure AI Search —
hybrid retrieval with semantic re-ranking, citations on every claim, and an
automated groundedness gate that fails the build on a quality regression.

The entire Azure footprint is Terraform. Nothing here was created in the portal.

> **Status: scaffolded, not yet measured.** The structure, infrastructure and
> harness are in place; the retrieval and generation internals are marked
> `TODO` with the relevant build block. Every `TBD` below is a number that will
> be filled in from a real run, not estimated. Honest placeholders beat
> invented results.

**Live endpoint:** _TBD_ · **Cost to run:** ~A$0/month (see [docs/costs.md](docs/costs.md))

---

## The result

> _TBD — the headline experiment, filled in after three live runs:_
>
> On a 60-question golden set over a NN-document corpus, adding semantic
> re-ranking on top of hybrid retrieval moved retrieval recall@5 from **A%** to
> **B%**, the share of answers with zero unsupported claims from **C%** to
> **D%**, and correct abstention on 10 unanswerable questions from **E/10** to
> **F/10**. Mean of 3 runs; generator `gpt-4.1-mini`, judge `gpt-4.1`;
> judge verdicts hand-checked on 20% of items with **G%** agreement.

One number, one controlled change, stated with its n and its caveats.
Raw runs in [`eval/reports/`](eval/reports), the committed baseline the gate
compares against in [`eval/baselines/`](eval/baselines).

## What this demonstrates

- **RAG with its failure modes understood** — not a happy-path demo. Six
  deliberate breakages, each measured: [docs/failure-modes.md](docs/failure-modes.md).
- **Evaluation as a build gate** — four metrics, a committed baseline, and a
  nightly job that fails on regression: [docs/evaluation.md](docs/evaluation.md).
- **Infrastructure as code, keyless** — Foundry, Search, Key Vault, Container
  Apps and least-privilege roles in Terraform; GitHub Actions authenticates to
  Azure via OIDC with no stored credential.

## Architecture

```
                  ┌────────────────────────┐
   question ─────▶│  API service           │  read-only identity
                  │  Container App         │  scales to zero when idle
                  └───────┬────────────────┘
                          │ managed identity, no keys
          ┌───────────────┴───────────────┐
          ▼                               ▼
 ┌──────────────────┐            ┌──────────────────┐
 │ Azure AI Search  │            │ Microsoft Foundry│
 │ BM25 + vector    │            │ gpt-4.1-mini     │
 │ → semantic rerank│            │ text-embedding-3 │
 └──────────────────┘            └──────────────────┘
          ▲                               ▲
          │ writes                        │ embeds
          │        ┌──────────────────────┴───┐
          └────────│  Ingestion job           │  write-scoped identity
                   │  Container Apps Job      │  runs to completion, no ingress
                   └───────┬──────────────────┘
                           │ reads
                   ┌───────▼──────────┐
                   │ Blob Storage     │  the source corpus
                   └──────────────────┘
```

Two deployables, sharing one Container Apps environment and one core library.
They are separate because they differ in lifecycle (per-request versus batch),
in sizing (0.25 vCPU versus 0.5), and above all in privilege: the API holds
`Search Index Data Reader` and no storage role at all, while only the job can
rebuild the index. `make roles` prints both role sets side by side.


A question is embedded, then one hybrid search request runs keyword and vector
matching together and returns 50 candidates. Those go to Azure's semantic
ranker, which reads the question and each passage together and reorders them;
the top 5 become the prompt context. The model answers only from those, cites
each claim, and emits a sentinel string when the passages do not contain the
answer.

Details and the reasoning behind each choice: [docs/architecture.md](docs/architecture.md).

## Repository layout

| Path | What it holds |
| --- | --- |
| [`libs/rag_core/`](libs/rag_core) | shared library: settings, clients, chunking, index schema |
| [`services/api/`](services/api) | the API service: retrieval, generation, FastAPI — read-only |
| [`services/ingest/`](services/ingest) | the ingestion job: sources, embedding cache, pipeline — the only writer |
| [`infra/`](infra) | Terraform: modules, the `dev` root, and the CI identity |
| [`eval/`](eval) | golden set, four metrics, judge prompts, the runner and the gate |
| [`.github/workflows/`](.github/workflows) | PR checks, Terraform plan, two deploys, run-ingest, nightly eval |
| [`docs/`](docs) | architecture, evaluation, failure modes, costs, onboarding |
| [`scripts/`](scripts) | bootstrap, teardown, cost check |

Each service's Dockerfile installs only its own extra from `pyproject.toml`, so
the API image contains no blob-storage client and the ingestion image contains
no web server. The privilege separation is enforced by image contents and Azure
roles, not by convention.

## Run it yourself

Needs: an Azure subscription, Terraform ≥ 1.9, Python 3.12, Azure CLI, Docker.

```bash
./scripts/bootstrap.sh          # read this, don't just run it

export TF_VAR_subscription_id=$(az account show --query id -o tsv)
export TF_VAR_ghcr_token=ghp_...                  # read:packages only

cd infra/envs/dev
cp terraform.tfvars.example terraform.tfvars      # set ghcr_username
terraform init && terraform apply

cd -
make install
make env                                          # .env from Terraform outputs
make ingest                                       # chunk, embed, push (locally)
make serve                                        # http://localhost:8000/docs
make eval                                         # the golden set
make roles                                        # what each deployable may do
```

Tear it down with `make destroy`, which also lists anything left behind.

## Cost

Every component is on a free SKU, an always-free monthly grant, or per-token
pricing measured in cents. Idle cost is effectively zero, so the stack can stay
up between interviews. Full breakdown, with the two traps (Azure Container
Registry has no free tier; Log Analytics ingestion is the one line item that
creeps): [docs/costs.md](docs/costs.md).

## New to the project?

[docs/onboarding.md](docs/onboarding.md) explains what RAG is, what each Azure
component does and why the design is shaped the way it is, assuming no prior
knowledge of any of it.

## What I'd do next

- **Query rewriting** — expand acronyms and resolve pronouns before retrieval;
  the failure-mode notes show multi-hop questions are where recall drops first.
- **A human-labelled eval set** — the judge is checked against a 20% sample;
  a fully labelled set would let me quote groundedness without that caveat.
- **Conversational memory** — single-turn today. Follow-up questions ("what
  about overseas?") need the previous turn folded into the query.
- **Private endpoints** — public endpoints with Entra ID auth are right for a
  portfolio project and wrong for regulated data.
