# infra

Every Azure resource in this project, as code. Nothing here was created in the portal.

```
infra/
├── modules/              reusable building blocks, one concern each
│   ├── foundry/          Microsoft Foundry account + project + model deployments
│   ├── search/           Azure AI Search (Free tier, semantic ranker on)
│   ├── storage/          Blob Storage for the source corpus
│   ├── keyvault/         the one real secret (ghcr pull token), RBAC mode
│   ├── identity/         a managed identity plus exactly the roles it is given
│   ├── container_app_env/ the Container Apps environment, shared by both workloads
│   ├── container_app/    the API service — read-only, public, scales to zero
│   └── ingest_job/       the ingestion job — write-scoped, batch, no ingress
├── envs/dev/             the root module you actually apply
└── cicd/                 the GitHub Actions OIDC identity (apply once, separately)
```

The `identity` module is generic: callers pass a map of role assignments. That
is why `envs/dev/main.tf` can show the API's read-only role set and the job's
write set next to each other — the asymmetry between them is the security
story, so it belongs where it can be read at a glance rather than hidden inside
a module.

## Why it is split this way

`envs/dev` is the root module: it owns the resource group, generates the random
suffix that makes globally-unique names unique, and wires the modules together.
Adding a `envs/prod` later means a new tfvars file, not a rewrite.

`cicd` is deliberately a *separate* root module. It creates an Entra ID app
registration, which needs different permissions and changes far less often than
the workload. Keeping it apart means a routine `terraform apply` on the workload
can never accidentally alter who is allowed to deploy.

## First run

```bash
az login
export TF_VAR_subscription_id=$(az account show --query id -o tsv)
export TF_VAR_ghcr_token=ghp_your_read_packages_token   # never in tfvars

cd envs/dev
cp terraform.tfvars.example terraform.tfvars   # set ghcr_username
terraform init
terraform plan -out tf.plan
terraform apply tf.plan
```

Then prove it round-trips, which is the single most convincing thing in this repo:

```bash
terraform destroy -auto-approve && terraform apply -auto-approve
```

## Known rough edges

- `semantic_search_sku` on the Free tier: if apply fails complaining about the
  semantic plan, drop that line from `modules/search` and enable semantic
  ranking through the REST API instead. Free tier *runs* the ranker; whether the
  plan is settable via ARM on Free has changed before.
- `rbac_authorization_enabled` in `modules/keyvault` is the azurerm 4.x name.
  On 3.x it is `enable_rbac_authorization`.
- Role assignments are eventually consistent. A fresh apply followed
  immediately by ingestion can 403 for a minute or two. Wait, then retry.
- `Search Index Data Contributor` covers documents; creating or deleting the
  index itself needs `Search Service Contributor`. The ingestion identity holds
  both. A `--recreate` run that is missing the second one fails with a 403 that
  looks identical to the first.
- Model names and versions in `modules/foundry/variables.tf` move fast. Check
  `az cognitiveservices account list-models` for what your region actually has
  before the first apply.
