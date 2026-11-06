variable "subscription_id" {
  description = "Set with: export TF_VAR_subscription_id=$(az account show --query id -o tsv)"
  type        = string
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "location" {
  description = "Sydney is australiaeast. Model deployments use GlobalStandard so capacity is not an issue."
  type        = string
  default     = "australiaeast"
}

variable "search_sku" {
  type    = string
  default = "free"
}

variable "search_index_name" {
  type    = string
  default = "corpus-v1"
}

variable "corpus_container_name" {
  type    = string
  default = "corpus"
}

variable "ghcr_username" {
  description = "Your GitHub username, for pulling the image from ghcr.io."
  type        = string
}

variable "ghcr_token" {
  description = "read:packages PAT. Pass via TF_VAR_ghcr_token, never in tfvars."
  type        = string
  sensitive   = true
}

variable "operator_principal_id" {
  description = "Object ID allowed to run ingestion locally. Null falls back to the caller."
  type        = string
  default     = null
}

variable "grant_operator_access" {
  description = <<-EOT
    Grant the operator the same roles the ingestion job has, so `make ingest`
    works from a laptop. Set false in CI, where the job should be started
    rather than the pipeline doing ingestion itself.
  EOT
  type    = bool
  default = true
}

variable "delete_after" {
  description = "Reminder tag, YYYY-MM-DD. Nothing enforces it; it is for your own teardown check."
  type        = string
  default     = "2026-12-31"
}
