output "id" {
  value = azurerm_user_assigned_identity.this.id
}

output "client_id" {
  description = "Pass to the workload as AZURE_CLIENT_ID so DefaultAzureCredential picks this identity."
  value       = azurerm_user_assigned_identity.this.client_id
}

output "principal_id" {
  value = azurerm_user_assigned_identity.this.principal_id
}

output "granted_roles" {
  description = "What this identity may do. Handy in a plan diff and in a demo."
  value       = { for k, v in var.role_assignments : k => v.role }
}
