variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "container_app_environment_id" {
  description = "Shared with the API service - see modules/container_app_env."
  type        = string
}

variable "image" {
  description = "Initial image. deploy-ingest.yml replaces this when ingestion code changes."
  type        = string
  default     = "mcr.microsoft.com/k8se/quickstart-jobs:latest"
}

variable "replica_timeout_in_seconds" {
  description = "Hard stop for one run. Long enough for the corpus, short enough that a hang fails."
  type        = number
  default     = 1800
}

variable "user_assigned_identity_id" {
  type = string
}

variable "managed_identity_client_id" {
  type = string
}

variable "ghcr_username" {
  type = string
}

variable "ghcr_token" {
  type      = string
  sensitive = true
}

variable "search_endpoint" {
  type = string
}

variable "search_index_name" {
  type = string
}

variable "foundry_endpoint" {
  type = string
}

variable "embedding_deployment_name" {
  type = string
}

variable "blob_endpoint" {
  type = string
}

variable "blob_container" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
