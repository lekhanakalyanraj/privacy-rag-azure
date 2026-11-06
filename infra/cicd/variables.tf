variable "subscription_id" {
  type = string
}

variable "github_owner" {
  description = "GitHub user or org that owns the repo."
  type        = string
}

variable "repository" {
  type    = string
  default = "privacy-rag-azure"
}

variable "default_branch" {
  type    = string
  default = "main"
}

variable "resource_group_name" {
  description = "Resource group the pipeline may manage. Must match the workload env."
  type        = string
  default     = "rg-rag-dev"
}
