# Architecture and design decisions

## Request path

1. **Embed the question** with the same deployment used at ingestion time.
   Different embedding models produce incompatible vector spaces, so a mismatch
   here degrades retrieval silently rather than loudly — nothing errors, results
   just get worse.
2. **One hybrid search request.** BM25 keyword scoring and vector similarity run
   together over the same documents and their rankings are fused. `top=50`.
3. **Semantic re-ranking.** The 50 candidates go to Azure's semantic ranker,
   which scores question and passage together. Keep 5.
4. **Generate** from those 5, with numbered citations and an abstention sentinel.
5. **Return the trace** — chunk ids, both scores, token usage — so a wrong
   answer can be attributed to retrieval or to generation without guessing.

## Decisions worth defending

### Two deployables, not one — and not four

The API service and the ingestion job are separate images, with separate
identities, deployed by separate workflows. The request path is *not* split
further.

Ingestion earns its own deployable on three independent grounds, any one of
which would be sufficient:

1. **Lifecycle.** It is batch. It runs for minutes on demand and exits. That is
   a Container Apps *Job*, which gives a replica timeout, a retry limit and a
   completion status. Modelling it as a service would give a container that
   keeps restarting.
2. **Sizing.** Minutes of sustained work versus sub-second bursts. 0.5 vCPU /
   1 GiB against 0.25 / 0.5. Co-located, one container is sized for neither.
3. **Privilege, which is the strongest reason.** Ingestion writes to the search
   index and reads the corpus; the API does neither. Split, the API's identity
   holds `Search Index Data Reader` and *no storage role at all*, and its image
   does not even contain `azure-storage-blob`. The container serving public
   traffic has no path to modifying the index — enforced by image contents and
   Azure RBAC rather than by anyone remembering not to call a function.

Run `make roles` to print both role sets side by side; the asymmetry is the
point, which is why the two role maps sit next to each other in
`infra/envs/dev/main.tf` rather than inside the identity module.

### Why retrieval and generation are *not* split

They are a seam, not a wire. `retrieve()` returns a plain list of `Passage`,
`answer.generate()` takes formatted text — the interface is clean enough to cut
at any time, and deliberately left uncut.

Microservices buy independent deploy cadence, independent scaling, and fault
isolation. Across retrieval and generation here, none of those applies: they
deploy together, scale together, and one is useless without the other. What
splitting them *would* cost is concrete — with `min_replicas = 0`, a service
calling a service means two chained cold starts in the request path, plus a
network hop on every warm request.

The conditions that would change the answer, written down so the decision can
be revisited rather than re-argued:

- a second consumer needs retrieval without generation
- re-ranking becomes GPU-bound and has to scale on a different axis from the
  generation calls
- retrieval and generation acquire genuinely different availability targets

None hold today. Knowing which ones would is the part worth demonstrating.


### Push-based ingestion, not an indexer + skillset
Azure AI Search can chunk and embed documents for you. On the Free tier that
path is capped at 20 documents per indexer per day with 1–3 minute run limits,
which makes it unusable here. Doing it in Python is also simply better for this
project: chunking is the highest-leverage decision in a RAG system and it should
be visible, tested and tunable rather than hidden behind a built-in skill. It
lives in `services/ingest/`, which is what makes it a job rather than a
background thread in the API.

### Hybrid, then re-rank — not one or the other
Keyword search wins on exact terms a user quotes. Vector search wins on
paraphrase. Each fails where the other works, so both run. Neither, though,
scores the passage *against the question* — they score it in isolation. The
re-ranker does, which is why it goes last and why it only sees a shortlist:
cheap and wide, then expensive and narrow.

### `candidate_k = 50`, `final_k = 5`
50 sets the ceiling on what re-ranking can possibly find; 5 is what the model
reads. Raising `final_k` dilutes attention across more context and tends to
*reduce* groundedness. Both are in `settings.py` precisely so they can be moved
and measured rather than argued about.

### An abstention sentinel, not a polite refusal
The prompt specifies the exact string `NOT_IN_PROVIDED_DOCUMENTS`. Detection is
then a string comparison instead of fuzzy matching on model prose. A metric that
depends on the model's choice of words is a metric that drifts as the model
changes underneath it.

### Managed identity, no keys
`DefaultAzureCredential` everywhere: locally it uses `az login`, in Azure the
container's user-assigned managed identity. One code path, so what is tested is
what runs. A secret that was never stored cannot leak. The search service has
`local_authentication_enabled = false`, which means admin keys do not exist to
be found.

### Deploying the job is not running it
`deploy-ingest.yml` updates the job definition; `run-ingest.yml` starts a run,
manually. Ingestion spends embedding tokens and rewrites the index the API is
serving from, so it is a decision rather than a side effect of merging code.
The run-ingest workflow waits for a terminal status instead of reporting
success on submission — a batch job that silently fails is worse than one that
never ran.

### Scale to zero
`min_replicas = 0`. Nothing runs and nothing is billed while idle; the first
request after a quiet period pays a cold start. For a portfolio endpoint that is
plainly the right trade, and it is worth being able to say *why* it is the wrong
trade for a latency-sensitive service.

### Terraform state in Azure, not on a laptop
A remote backend is configured (commented out until the storage account exists).
Not strictly necessary for one developer — but "my state was local" is a bad
answer to an obvious interview question.

## Things deliberately not done

- **No private endpoints.** Public endpoints with Entra ID auth are right for a
  portfolio project. For regulated data they are not, and the Terraform is
  structured so adding them touches one module.
- **No conversational memory.** Single-turn. Multi-turn needs query rewriting
  to resolve references, which is a different problem than the one being shown.
- **No re-ranking model of my own.** Azure's ranker is good and free on this
  tier. Training one would demonstrate something this project is not about.
