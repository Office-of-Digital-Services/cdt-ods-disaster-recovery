# Diagnostic settings for the Application Gateway
resource "azurerm_monitor_diagnostic_setting" "app_gateway" {
  name                       = "${var.diagnostic_setting_prefix}-app-gateway"
  target_resource_id         = azurerm_application_gateway.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category_group = "allLogs"
  }
}
