variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "role_assignments" {
  description = <<-EOT
    Roles to grant this identity, keyed by a short name that shows up in the
    Terraform plan. Built-in role definition *names* rather than GUIDs, so the
    intent is readable in a diff.
  EOT
  type = map(object({
    scope = string
    role  = string
  }))
  default = {}
}

variable "tags" {
  type    = map(string)
  default = {}
}
