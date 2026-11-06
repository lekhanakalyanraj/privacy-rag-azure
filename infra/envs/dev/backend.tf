# Remote state.
#
# Left commented out so the very first `terraform apply` works with local
# state and no chicken-and-egg problem. Once the storage account exists,
# create a `tfstate` container in it, uncomment this, and run
# `terraform init -migrate-state`.
#
# Why bother for a solo project: it is the thing an interviewer asks about, and
# the answer "state lived on my laptop" is a bad one.

# terraform {
#   backend "azurerm" {
#     resource_group_name  = "rg-rag-dev"
#     storage_account_name = "strag<suffix>"
#     container_name       = "tfstate"
#     key                  = "dev.terraform.tfstate"
#     use_azuread_auth     = true
#   }
# }
