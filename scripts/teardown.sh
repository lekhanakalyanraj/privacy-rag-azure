#!/usr/bin/env bash
# Destroy everything and prove it is gone.
#
# The stack idles at roughly zero, so this is not urgent for cost reasons.
# Run it anyway, at least once, on purpose: a destroy-then-apply round trip is
# the strongest evidence in the repo that the infrastructure really is code.
set -euo pipefail

TF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../infra/envs/dev" && pwd)"
cd "$TF_DIR"

echo "==> Resources about to be destroyed"
terraform state list || { echo "No state here - nothing to destroy."; exit 0; }

read -rp "Destroy all of the above? [y/N] " reply
[[ "$reply" == "y" || "$reply" == "Y" ]] || { echo "Aborted."; exit 0; }

terraform destroy -auto-approve

echo
echo "==> Resource groups still tagged for this project"
az group list \
  --query "[?tags.project=='azure-rag-foundry'].{name:name, state:properties.provisioningState}" \
  -o table

echo
echo "==> Soft-deleted Key Vaults (these hold the name until purged)"
az keyvault list-deleted --query "[].{name:name, scheduledPurge:properties.scheduledPurgeDate}" -o table

echo
echo "Done. Anything listed above still exists."
