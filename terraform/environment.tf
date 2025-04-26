locals {
  is_prod            = terraform.workspace == "default"
  is_test            = terraform.workspace == "test"
  is_dev             = !(local.is_prod || local.is_test)
  env_name           = local.is_prod ? "prod" : terraform.workspace
  env_letter         = upper(substr(local.env_name, 0, 1))
  hostname           = local.is_prod ? "recovery.cdt.ca.gov" : "${local.env_name}.recovery.cdt.ca.gov"
  secret_http_prefix = "https://KV-CDT-PUB-DDRC-${local.env_letter}-001.vault.azure.net/secrets"
}

data "azurerm_resource_group" "main" {
  name = "RG-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
}

resource "azurerm_container_app_environment" "main" {
  name                       = "CAE-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  location                   = data.azurerm_resource_group.main.location
  resource_group_name        = data.azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_container_app_environment_storage" "config" {
  account_name                 = azurerm_storage_account.main.name
  access_key                   = azurerm_storage_account.main.primary_access_key
  access_mode                  = "ReadOnly"
  container_app_environment_id = azurerm_container_app_environment.main.id
  name                         = azurerm_storage_share.config.name
  share_name                   = azurerm_storage_share.config.name
}
