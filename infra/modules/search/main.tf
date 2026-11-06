# Azure AI Search, Free tier: 50 MB, 3 indexes, one service per subscription.
# Vectors and the semantic ranker both work on Free; replicas/partitions cannot
# be set, so they are absent. Skillset enrichment is capped at 20 docs/day,
# which is why ingestion is a Python job. See docs/costs.md.

resource "azurerm_search_service" "this" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku

  # Keyless by default: the app and CI use Entra ID, never an admin key.
  local_authentication_enabled = var.local_authentication_enabled

  # If apply fails on Free, drop this and enable the ranker via the REST API.
  semantic_search_sku = var.semantic_search_sku

  tags = var.tags
}
