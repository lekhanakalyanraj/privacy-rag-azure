# Holds the one genuine secret: the ghcr.io pull token. Endpoints and
# deployment names are configuration, not secrets.
# RBAC mode rather than access policies - one fewer permission model.

resource "azurerm_key_vault" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  tenant_id           = var.tenant_id
  sku_name            = "standard"

  # azurerm < 4.x calls this argument `enable_rbac_authorization`.
  rbac_authorization_enabled = true

  # So `terraform destroy` leaves a clean subscription and a reusable name.
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  tags = var.tags
}
