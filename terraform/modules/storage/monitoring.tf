# Diagnostic settings for the storage account
resource "azurerm_monitor_diagnostic_setting" "storage" {
  name                       = "${var.diagnostic_setting_prefix}-storage"
  target_resource_id         = azurerm_storage_account.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_metric {
    category = "Transaction"
  }
}
