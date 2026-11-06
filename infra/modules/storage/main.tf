# Blob Storage holds the source corpus. The ingestion pipeline reads from here.

resource "azurerm_storage_account" "this" {
  name                            = var.name
  resource_group_name             = var.resource_group_name
  location                        = var.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS" # cheapest; this data is reproducible
  account_kind                    = "StorageV2"
  https_traffic_only_enabled      = true
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false

  # Enabled only so Terraform can manage the container below. The workload
  # reads blobs with a managed identity and never uses a key.
  shared_access_key_enabled = true

  tags = var.tags
}

resource "azurerm_storage_container" "corpus" {
  name                  = var.container_name
  storage_account_id    = azurerm_storage_account.this.id
  container_access_type = "private"
}
