output "id" {
  value = azurerm_container_app_job.this.id
}

output "name" {
  description = "Start a run with: az containerapp job start --name <this> --resource-group <rg>"
  value       = azurerm_container_app_job.this.name
}
