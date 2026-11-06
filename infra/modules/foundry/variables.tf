variable "name" {
  description = "Globally unique name for the Foundry account (also used as the DNS subdomain)."
  type        = string
}

variable "project_name" {
  description = "Foundry project name."
  type        = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "local_authentication_enabled" {
  description = "Allow API-key auth. Set false once everything uses Entra ID."
  type        = bool
  default     = true
}

variable "chat_deployment_name" {
  type    = string
  default = "gpt-4-1-mini"
}

variable "chat_model_name" {
  type    = string
  default = "gpt-4.1-mini"
}

variable "chat_model_version" {
  type    = string
  default = "2025-04-14"
}

variable "chat_capacity" {
  description = "Thousands of tokens per minute. 1 is plenty for an eval harness."
  type        = number
  default     = 1
}

variable "embedding_deployment_name" {
  type    = string
  default = "text-embedding-3-small"
}

variable "embedding_model_name" {
  type    = string
  default = "text-embedding-3-small"
}

variable "embedding_model_version" {
  type    = string
  default = "1"
}

variable "embedding_capacity" {
  type    = number
  default = 1
}

variable "tags" {
  type    = map(string)
  default = {}
}
