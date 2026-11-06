#!/usr/bin/env bash
# One-time setup, in the order things actually have to happen.
# Read it rather than running it blind - each step is a decision.
set -euo pipefail

echo "1. Sign in and pin the subscription"
az login
az account show --query "{name:name, id:id, state:state}" -o table
export TF_VAR_subscription_id=$(az account show --query id -o tsv)

echo
echo "2. Budget alert at AUD 10"
echo "   Budgets ALERT, they do not stop spend. On a free-trial subscription the"
echo "   spending limit is what actually protects you - leave it on."
echo "   Portal: Cost Management > Budgets > Add"

echo
echo "3. Confirm the models you want exist in this region"
az cognitiveservices account list-models \
  --name "<any-existing-foundry-account>" \
  --resource-group "<its-rg>" \
  --query "[?contains(name,'mini') || contains(name,'embedding')].{name:name, version:version, sku:skus[0].name}" \
  -o table 2>/dev/null || echo "   (skip until the first account exists; then re-run to verify names)"

echo
echo "4. ghcr pull token: GitHub > Settings > Developer settings > Tokens"
echo "   Scope: read:packages only. Then: export TF_VAR_ghcr_token=ghp_..."

echo
echo "5. Apply"
echo "   cd infra/envs/dev && terraform init && terraform plan -out tf.plan && terraform apply tf.plan"

echo
echo "6. CI identity (once, separately - it creates an Entra ID app registration)"
echo "   cd infra/cicd && terraform init && terraform apply"
echo "   then set the three GitHub variables it outputs"
