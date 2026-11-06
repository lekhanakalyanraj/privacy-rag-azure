# Add these three as GitHub repository *variables* (not secrets - none of them
# is sensitive, and that is the whole point of OIDC):
#
#   gh variable set AZURE_CLIENT_ID       --body "$(terraform output -raw client_id)"
#   gh variable set AZURE_TENANT_ID       --body "$(terraform output -raw tenant_id)"
#   gh variable set AZURE_SUBSCRIPTION_ID --body "$(terraform output -raw subscription_id)"

output "client_id" {
  value = azuread_application.ci.client_id
}

output "tenant_id" {
  value = data.azurerm_subscription.current.tenant_id
}

output "subscription_id" {
  value = var.subscription_id
}
