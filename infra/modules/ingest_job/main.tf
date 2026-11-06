# The ingestion job. A Container Apps *Job*, not an app: it runs to completion
# and exits, so it wants a timeout, a retry limit and a completion status rather
# than a container that keeps restarting.
#
# Sized larger than the API because the work is batch. Manual trigger, since the
# corpus changes rarely - swap in schedule_trigger_config to run it on a cron
# instead (only one trigger block is allowed). See docs/architecture.md.

resource "azurerm_container_app_job" "this" {
  name                         = var.name
  location                     = var.location
  resource_group_name          = var.resource_group_name
  container_app_environment_id = var.container_app_environment_id

  # Long enough for a few hundred chunks; short enough that a hang fails.
  replica_timeout_in_seconds = var.replica_timeout_in_seconds
  replica_retry_limit        = 1

  manual_trigger_config {
    parallelism              = 1
    replica_completion_count = 1
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [var.user_assigned_identity_id]
  }

  secret {
    name  = "ghcr-token"
    value = var.ghcr_token
  }

  registry {
    server               = "ghcr.io"
    username             = var.ghcr_username
    password_secret_name = "ghcr-token"
  }

  template {
    container {
      name   = "ingest"
      image  = var.image
      cpu    = 0.5
      memory = "1Gi"

      # Note this client id differs from the API's - that is the split.
      env {
        name  = "AZURE_CLIENT_ID"
        value = var.managed_identity_client_id
      }
      env {
        name  = "SEARCH_ENDPOINT"
        value = var.search_endpoint
      }
      env {
        name  = "SEARCH_INDEX_NAME"
        value = var.search_index_name
      }
      env {
        name  = "FOUNDRY_ENDPOINT"
        value = var.foundry_endpoint
      }
      env {
        name  = "EMBEDDING_DEPLOYMENT"
        value = var.embedding_deployment_name
      }
      env {
        name  = "BLOB_ENDPOINT"
        value = var.blob_endpoint
      }
      env {
        name  = "BLOB_CONTAINER"
        value = var.blob_container
      }
    }
  }

  tags = var.tags

  # deploy-ingest.yml owns the image tag.
  lifecycle {
    ignore_changes = [template[0].container[0].image]
  }
}
