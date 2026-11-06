# Shared by the API service and the ingestion job, so neither owns the
# environment the other depends on.
#
# No Log Analytics workspace: the environment is free, log ingestion is not.

resource "azurerm_container_app_environment" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}
