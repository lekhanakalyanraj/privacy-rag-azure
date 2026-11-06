variable "name" {
  type = string
}

variable "container_app_environment_id" {
  description = "Shared with the ingestion job - see modules/container_app_env."
  type        = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "image" {
  description = "Initial image. The deploy workflow replaces this on every merge to main."
  type        = string
  default     = "mcr.microsoft.com/k8se/quickstart:latest"
}

variable "target_port" {
  type    = number
  default = 8000
}

variable "user_assigned_identity_id" {
  type = string
}

variable "managed_identity_client_id" {
  type = string
}

variable "ghcr_username" {
  description = "Your GitHub username."
  type        = string
}

variable "ghcr_token" {
  description = "A read:packages PAT. Keep it out of tfvars - pass via TF_VAR_ghcr_token."
  type        = string
  sensitive   = true
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

variable "chat_deployment_name" {
  type = string
}

variable "embedding_deployment_name" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
