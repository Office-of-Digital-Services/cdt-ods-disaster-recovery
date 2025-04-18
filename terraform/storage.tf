resource "azurerm_storage_account" "main" {
  name                             = "sacdtddrc${lower(local.env_letter)}001"
  location                         = data.azurerm_resource_group.main.location
  resource_group_name              = data.azurerm_resource_group.main.name
  account_tier                     = "Standard"
  account_replication_type         = "RAGRS"
  cross_tenant_replication_enabled = false

  blob_properties {
    last_access_time_enabled = true
    versioning_enabled       = true

    container_delete_retention_policy {
      days = 7
    }

    delete_retention_policy {
      days = 7
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_storage_share" "postgres" {
  name               = lower("sts-cdt-pub-vip-ddrc-${local.env_letter}-postgres")
  storage_account_id = azurerm_storage_account.main.id
  # in GB
  quota = 5
  # Access Tier can be TransactionOptimized, Hot, Cool.
  # TransactionOptimized is good for frequent access.
  access_tier = "TransactionOptimized"
}
