# Dev environment root module.  terraform init && terraform apply
#
# Two deployables over shared backing resources: a read-only public API and a
# write-scoped ingestion job. The role maps below are why they are separate.
# Everything here is free or free-tier - see docs/costs.md.

data "azurerm_client_config" "current" {}

# Several of these resources need globally unique names.
resource "random_string" "suffix" {
  length  = 6
  lower   = true
  upper   = false
  numeric = true
  special = false
}

locals {
  suffix = random_string.suffix.result

  tags = {
    project      = "privacy-rag-azure"
    environment  = "dev"
    managed_by   = "terraform"
    delete_after = var.delete_after # scripts/teardown.sh greps this
  }
}

resource "azurerm_resource_group" "this" {
  name     = "rg-rag-${var.environment}"
  location = var.location
  tags     = local.tags
}

# --- Backing resources, shared by both deployables ---

module "storage" {
  source = "../../modules/storage"

  name                = "strag${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  container_name      = var.corpus_container_name
  tags                = local.tags
}

module "search" {
  source = "../../modules/search"

  name                = "srch-rag-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  sku                 = var.search_sku
  tags                = local.tags
}

module "foundry" {
  source = "../../modules/foundry"

  name                = "fdy-rag-${local.suffix}"
  project_name        = "rag-assistant"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.tags
}

module "keyvault" {
  source = "../../modules/keyvault"

  name                = "kv-rag-${local.suffix}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  tags                = local.tags
}

module "container_app_env" {
  source = "../../modules/container_app_env"

  name                = "cae-rag-${var.environment}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.tags
}

# ---------------------------------------------------------------------------
# Identities. Read the two role maps side by side: the API cannot write to the
# index or reach the corpus; only the job can. Neither holds a password.
# ---------------------------------------------------------------------------

module "api_identity" {
  source = "../../modules/identity"

  name                = "id-rag-api-${var.environment}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.tags

  # No storage role: once ingestion moved out, the API stopped needing the corpus.
  role_assignments = {
    search_read    = { scope = module.search.id, role = "Search Index Data Reader" }
    foundry_models = { scope = module.foundry.id, role = "Cognitive Services OpenAI User" }
    vault_secrets  = { scope = module.keyvault.id, role = "Key Vault Secrets User" }
  }
}

module "ingest_identity" {
  source = "../../modules/identity"

  name                = "id-rag-ingest-${var.environment}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  tags                = local.tags

  # search_admin is separate from search_write: index *definitions* are a
  # different permission from index *documents*, and --recreate needs both.
  # No vault role - the image pull secret is resolved by the platform.
  role_assignments = {
    search_write   = { scope = module.search.id, role = "Search Index Data Contributor" }
    search_admin   = { scope = module.search.id, role = "Search Service Contributor" }
    blob_read      = { scope = module.storage.id, role = "Storage Blob Data Reader" }
    foundry_models = { scope = module.foundry.id, role = "Cognitive Services OpenAI User" }
  }
}

# The operator, so `make ingest` works from a laptop with no keys. Same roles as
# the job, or local success stops predicting deployed success.

locals {
  operator_principal_id = coalesce(
    var.operator_principal_id, data.azurerm_client_config.current.object_id
  )

  operator_roles = {
    search_write   = { scope = module.search.id, role = "Search Index Data Contributor" }
    search_admin   = { scope = module.search.id, role = "Search Service Contributor" }
    blob_write     = { scope = module.storage.id, role = "Storage Blob Data Contributor" }
    foundry_models = { scope = module.foundry.id, role = "Cognitive Services OpenAI User" }
  }
}

resource "azurerm_role_assignment" "operator" {
  for_each = var.grant_operator_access ? local.operator_roles : {}

  scope                = each.value.scope
  role_definition_name = each.value.role
  principal_id         = local.operator_principal_id
}

# --- Deployables ---

module "api" {
  source = "../../modules/container_app"

  name                = "ca-rag-api-${var.environment}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name

  container_app_environment_id = module.container_app_env.id

  user_assigned_identity_id  = module.api_identity.id
  managed_identity_client_id = module.api_identity.client_id

  ghcr_username = var.ghcr_username
  ghcr_token    = var.ghcr_token

  search_endpoint           = module.search.endpoint
  search_index_name         = var.search_index_name
  foundry_endpoint          = module.foundry.endpoint
  chat_deployment_name      = module.foundry.chat_deployment_name
  embedding_deployment_name = module.foundry.embedding_deployment_name

  tags = local.tags
}

module "ingest_job" {
  source = "../../modules/ingest_job"

  name                = "cj-rag-ingest-${var.environment}"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name

  container_app_environment_id = module.container_app_env.id

  user_assigned_identity_id  = module.ingest_identity.id
  managed_identity_client_id = module.ingest_identity.client_id

  ghcr_username = var.ghcr_username
  ghcr_token    = var.ghcr_token

  search_endpoint           = module.search.endpoint
  search_index_name         = var.search_index_name
  foundry_endpoint          = module.foundry.endpoint
  embedding_deployment_name = module.foundry.embedding_deployment_name
  blob_endpoint             = module.storage.blob_endpoint
  blob_container            = module.storage.container_name

  tags = local.tags
}
