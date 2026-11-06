# Microsoft Foundry: account, project, and the model deployments.
# No base charge; you pay per token, so capacity is deliberately tiny.

resource "azurerm_cognitive_account" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "AIServices"
  sku_name            = "S0"

  # Required for project management and stateful Foundry features.
  custom_subdomain_name      = var.name
  project_management_enabled = true

  # Flip to false once everything authenticates with Entra ID.
  local_authentication_enabled = var.local_authentication_enabled

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

resource "azurerm_cognitive_account_project" "this" {
  name                 = var.project_name
  cognitive_account_id = azurerm_cognitive_account.this.id
  location             = var.location

  identity {
    type = "SystemAssigned"
  }
}

# GlobalStandard: regional capacity in australiaeast is often unavailable.
resource "azurerm_cognitive_deployment" "chat" {
  name                 = var.chat_deployment_name
  cognitive_account_id = azurerm_cognitive_account.this.id

  sku {
    name     = "GlobalStandard"
    capacity = var.chat_capacity
  }

  model {
    format  = "OpenAI"
    name    = var.chat_model_name
    version = var.chat_model_version
  }
}

resource "azurerm_cognitive_deployment" "embedding" {
  name                 = var.embedding_deployment_name
  cognitive_account_id = azurerm_cognitive_account.this.id

  sku {
    name     = "Standard"
    capacity = var.embedding_capacity
  }

  model {
    format  = "OpenAI"
    name    = var.embedding_model_name
    version = var.embedding_model_version
  }
}
