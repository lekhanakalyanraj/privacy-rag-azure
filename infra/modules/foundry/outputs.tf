output "id" {
  value = azurerm_cognitive_account.this.id
}

output "endpoint" {
  description = "Base endpoint the SDK talks to."
  value       = azurerm_cognitive_account.this.endpoint
}

output "project_id" {
  value = azurerm_cognitive_account_project.this.id
}

output "chat_deployment_name" {
  value = azurerm_cognitive_deployment.chat.name
}

output "embedding_deployment_name" {
  value = azurerm_cognitive_deployment.embedding.name
}
