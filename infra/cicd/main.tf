# The CI identity, so even the pipeline's Azure access is code.
#
# GitHub Actions gets no stored password: it mints a short-lived OIDC token
# asserting which repo and branch it is, and the federated credentials below
# tell Entra ID to trust exactly that. Nothing long-lived exists to leak.
#
# A separate root module - different lifecycle, different permissions. Apply
# once:  cd infra/cicd && terraform init && terraform apply

terraform {
  required_version = ">= 1.9.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.20"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  subscription_id = var.subscription_id
  features {}
}

provider "azuread" {}

data "azurerm_subscription" "current" {}

resource "azuread_application" "ci" {
  display_name     = "gh-${var.repository}-ci"
  sign_in_audience = "AzureADMyOrg"
}

resource "azuread_service_principal" "ci" {
  client_id = azuread_application.ci.client_id
}

# Deploys from the default branch.
resource "azuread_application_federated_identity_credential" "main_branch" {
  application_id = azuread_application.ci.id
  display_name   = "gh-main-branch"
  description    = "Deploys from refs/heads/${var.default_branch}"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:${var.github_owner}/${var.repository}:ref:refs/heads/${var.default_branch}"
}

# Separate credential for pull requests, so it can be scoped down later.
resource "azuread_application_federated_identity_credential" "pull_request" {
  application_id = azuread_application.ci.id
  display_name   = "gh-pull-request"
  description    = "terraform plan on pull requests"
  audiences      = ["api://AzureADTokenExchange"]
  issuer         = "https://token.actions.githubusercontent.com"
  subject        = "repo:${var.github_owner}/${var.repository}:pull_request"
}

# Scoped to the one resource group, not the subscription.
resource "azurerm_role_assignment" "ci_rg_contributor" {
  scope                = "${data.azurerm_subscription.current.id}/resourceGroups/${var.resource_group_name}"
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.ci.object_id
}

# Contributor alone cannot create role assignments.
resource "azurerm_role_assignment" "ci_rbac_admin" {
  scope                = "${data.azurerm_subscription.current.id}/resourceGroups/${var.resource_group_name}"
  role_definition_name = "Role Based Access Control Administrator"
  principal_id         = azuread_service_principal.ci.object_id
}
