# Diagnostic settings for the Key Vault
resource "azurerm_monitor_diagnostic_setting" "key_vault" {
  name                       = "${var.diagnostic_setting_prefix}-kv"
  target_resource_id         = azurerm_key_vault.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category_group = "allLogs"
  }

  enabled_log {
    category_group = "audit"
  }
}
