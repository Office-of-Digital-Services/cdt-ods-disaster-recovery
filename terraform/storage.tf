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

resource "azurerm_storage_share" "config" {
  name               = "config"
  storage_account_id = azurerm_storage_account.main.id
  quota              = 1
  access_tier        = "Cool"
}

resource "azurerm_storage_share" "requests" {
  name               = "requests"
  storage_account_id = azurerm_storage_account.main.id
  quota              = 5
}
