variable "name" {
  description = "Globally unique storage account name (3-24 chars, lowercase alphanumeric)."
  type        = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "container_name" {
  type    = string
  default = "corpus"
}

variable "tags" {
  type    = map(string)
  default = {}
}
