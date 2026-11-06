#!/usr/bin/env bash
# What this project has actually cost. Fills in the real numbers for docs/costs.md.
#
# Usage: ./scripts/cost.sh [days]   (default 30)
set -euo pipefail

DAYS="${1:-30}"
START=$(date -u -v-"${DAYS}"d +%Y-%m-%d 2>/dev/null || date -u -d "${DAYS} days ago" +%Y-%m-%d)
END=$(date -u +%Y-%m-%d)

echo "==> Usage from $START to $END"
az consumption usage list \
  --start-date "$START" --end-date "$END" \
  --query "[].{service:meterDetails.meterCategory, meter:meterDetails.meterName, cost:pretaxCost, currency:currency}" \
  -o table 2>/dev/null || {
    echo "az consumption is unavailable on some subscription types."
    echo "Check Cost Management in the portal instead: https://portal.azure.com/#view/Microsoft_Azure_CostManagement"
  }

echo
echo "==> Budgets configured"
az consumption budget list --query "[].{name:name, amount:amount, spent:currentSpend.amount}" -o table 2>/dev/null || true
