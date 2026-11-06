# The API service. min_replicas = 0, so it costs nothing idle and pays a cold
# start on the first request after a quiet period.
#
# Read-only by construction: its identity holds Search Index Data Reader and the
# image contains no ingestion code. Images come from ghcr.io - ACR has no free tier.

resource "azurerm_container_app" "this" {
  name                         = var.name
  container_app_environment_id = var.container_app_environment_id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  tags                         = var.tags

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

  ingress {
    external_enabled = true
    target_port      = var.target_port
    transport        = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = 0
    max_replicas = 1

    container {
      name   = "api"
      image  = var.image
      cpu    = 0.25
      memory = "0.5Gi"

      # Configuration, not secrets.
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
        name  = "CHAT_DEPLOYMENT"
        value = var.chat_deployment_name
      }
      env {
        name  = "EMBEDDING_DEPLOYMENT"
        value = var.embedding_deployment_name
      }

      liveness_probe {
        transport = "HTTP"
        port      = var.target_port
        path      = "/healthz"
      }

      readiness_probe {
        transport = "HTTP"
        port      = var.target_port
        path      = "/healthz"
      }
    }
  }

  # deploy-api.yml owns the image tag.
  lifecycle {
    ignore_changes = [template[0].container[0].image]
  }
}
