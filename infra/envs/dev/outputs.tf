output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "app_url" {
  description = "Public endpoint. Try: curl $(terraform output -raw app_url)/healthz"
  value       = module.api.url
}

output "container_app_name" {
  value = module.api.name
}

output "ingest_job_name" {
  description = "Run it: az containerapp job start --name <this> --resource-group <rg>"
  value       = module.ingest_job.name
}

# Consumed by `make env`, `make ingest` and the eval harness, so configuration
# is never hand-copied between Terraform and the application.
output "app_env" {
  description = "Everything the API, the job and the eval harness need to connect."
  value = {
    SEARCH_ENDPOINT      = module.search.endpoint
    SEARCH_INDEX_NAME    = var.search_index_name
    FOUNDRY_ENDPOINT     = module.foundry.endpoint
    CHAT_DEPLOYMENT      = module.foundry.chat_deployment_name
    EMBEDDING_DEPLOYMENT = module.foundry.embedding_deployment_name
    BLOB_ENDPOINT        = module.storage.blob_endpoint
    BLOB_CONTAINER       = module.storage.container_name
    KEY_VAULT_URI        = module.keyvault.uri
  }
}

# The security story, in a form you can paste into a README or read out in an
# interview. Worth an output of its own precisely because the asymmetry is the
# reason the two deployables are separate.
output "identities" {
  description = "What each deployable is permitted to do."
  value = {
    api = {
      client_id = module.api_identity.client_id
      roles     = module.api_identity.granted_roles
    }
    ingest = {
      client_id = module.ingest_identity.client_id
      roles     = module.ingest_identity.granted_roles
    }
  }
}
