.PHONY: help install lint test env corpus ingest ingest-job serve eval eval-replay plan apply destroy docker roles
.DEFAULT_GOAL := help

TF_DIR := infra/envs/dev
PY     := .venv/bin

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Create the venv and install everything (core + both services + dev)
	python3 -m venv .venv
	$(PY)/pip install -e ".[dev]"

lint: ## Ruff + mypy across the core and both services
	$(PY)/ruff check libs services eval scripts
	$(PY)/ruff format --check libs services eval scripts
	$(PY)/mypy libs services

test: ## Unit tests (no Azure, no network)
	$(PY)/pytest

env: ## Write .env from Terraform outputs
	cd $(TF_DIR) && terraform output -json app_env | \
	  jq -r 'to_entries[] | "\(.key)=\(.value)"' > $(CURDIR)/.env
	@echo "wrote .env"

roles: ## Show what each deployable is permitted to do
	cd $(TF_DIR) && terraform output -json identities | jq

corpus: ## Fetch the OAIC guidance chapters into data/sample-corpus
	$(PY)/python scripts/fetch_corpus.py

ingest: ## Run ingestion locally against the dev index
	$(PY)/python -m rag_ingest --local data/sample-corpus

ingest-job: ## Start the ingestion job in Azure and follow it
	az containerapp job start \
	  --name $$(cd $(TF_DIR) && terraform output -raw ingest_job_name) \
	  --resource-group $$(cd $(TF_DIR) && terraform output -raw resource_group_name)

serve: ## Run the API locally on :8000
	$(PY)/uvicorn rag_api.main:app --reload --port 8000

eval: ## Live eval against the deployed app
	$(PY)/python eval/run_eval.py --live \
	  --api-url $$(cd $(TF_DIR) && terraform output -raw app_url)

eval-replay: ## Re-score recorded fixtures (what CI runs on PRs)
	$(PY)/python eval/run_eval.py --replay

plan: ## terraform plan
	cd $(TF_DIR) && terraform plan -out tf.plan

apply: ## terraform apply
	cd $(TF_DIR) && terraform apply tf.plan

destroy: ## Tear everything down
	./scripts/teardown.sh

docker: ## Build both images locally
	docker build -f services/api/Dockerfile    -t rag-api:dev .
	docker build -f services/ingest/Dockerfile -t rag-ingest:dev .
