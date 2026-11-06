variable "name" {
  description = "Globally unique search service name."
  type        = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "sku" {
  description = "Keep this 'free' unless you knowingly want a bill."
  type        = string
  default     = "free"

  validation {
    condition     = contains(["free", "basic", "standard"], var.sku)
    error_message = "Use 'free' for this project; 'basic' and upward are billed hourly."
  }
}

variable "semantic_search_sku" {
  description = "Semantic ranker plan. 'free' includes a monthly request allowance."
  type        = string
  default     = "free"
}

variable "local_authentication_enabled" {
  description = "Allow admin/query key auth. False forces Entra ID everywhere."
  type        = bool
  default     = false
}

variable "tags" {
  type    = map(string)
  default = {}
}
