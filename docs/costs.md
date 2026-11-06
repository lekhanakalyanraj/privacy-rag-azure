# Cost

Verified against Microsoft documentation on 6 Nov 2026. Re-check before you
apply: tiers and free grants change.

| Resource | Why it is free | The trap |
| --- | --- | --- |
| Azure AI Search | `sku = "free"` — one per subscription, 50 MB, 3 indexes. Vector fields supported. **Semantic ranker runs on Free.** | 50 MB total. Skillset enrichment is capped at 20 docs/indexer/day, which is why ingestion is a Python push pipeline. A free service may be deleted after long inactivity. |
| Microsoft Foundry | No base charge on the account, project or deployment. Pay per token. | `gpt-4.1-mini` ≈ $0.40/$1.60 per 1M tokens in/out (third-party trackers — confirm officially). A 60-question run ≈ **under $0.20**. |
| Blob Storage | 5 GB hot LRS free for 12 months on a new account; ~$0.02/GB-month after. | Nothing at this size. |
| Container Apps | Always-free per subscription per month: 180,000 vCPU-s, 360,000 GiB-s, 2M requests. `min_replicas = 0` barely touches it. | The environment is free; **Log Analytics ingestion is not.** No workspace is attached here. |
| Key Vault | Standard has no base charge; ~$0.03 per 10,000 operations. | Certificates cost money. None are provisioned. |
| Container registry | **ghcr.io, not ACR.** | Azure Container Registry has **no free tier** — Basic is ~$5/month. This is the single easiest accidental charge on this stack. |
| GitHub Actions | Unlimited minutes on a public repository. | Private repos consume quota. |

**Idle cost: effectively A$0/month.** The stack can stay up between interviews.

## Actual spend

Run `./scripts/cost.sh` and paste the output here. Real numbers beat the table
above, and a cost section with a real figure in it reads very differently from
one without.

```
TBD
```

## Guardrails in place

- Free-trial subscription spending limit left **on**. Budgets only alert; the
  spending limit is the only thing that actually stops spend.
- A$10 budget with alerts at 50 / 80 / 100%.
- `delete_after` tag on every resource, so `scripts/teardown.sh` can list
  anything that outlived its intended life.
- Embeddings cached on disk by content hash — re-ingestion after a chunking
  tweak only pays for chunks that changed.
- Pull requests run the eval in replay mode, so CI never spends tokens.

## Credit notes

A new Azure account gets **$200 for 30 days** plus 12-month free services, one
per customer. Azure for Students ($100, no card) is better if it still verifies
— worth trying first.

When the credit or the 30 days runs out, Azure disables the subscription rather
than charging you. Continuing means moving to pay-as-you-go, which has no hard
cap — so set the budget alerts before, not after.
