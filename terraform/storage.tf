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

resource "azurerm_storage_share" "web" {
  name               = "web"
  storage_account_id = azurerm_storage_account.main.id
  quota              = 1
}

resource "azurerm_container_app_environment_storage" "web" {
  account_name                 = azurerm_storage_account.main.name
  access_key                   = azurerm_storage_account.main.primary_access_key
  access_mode                  = "ReadOnly"
  container_app_environment_id = azurerm_container_app_environment.main.id
  name                         = azurerm_storage_share.web.name
  share_name                   = azurerm_storage_share.web.name
}
