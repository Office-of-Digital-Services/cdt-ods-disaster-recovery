# This module deploys a complete, privately networked, and monitored PostgreSQL instance.

resource "azurerm_postgresql_flexible_server" "main" {
  name                = var.server_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku_name            = var.sku_name
  storage_mb          = var.storage_mb
  storage_tier        = var.storage_tier
  version             = "16"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  authentication {
    active_directory_auth_enabled = false
    password_auth_enabled         = true
  }
  public_network_access_enabled = false
  administrator_login           = var.administrator_login
  administrator_password        = azurerm_key_vault_secret.postgres_admin_password.value

  lifecycle {
    ignore_changes = [tags]
  }
}
