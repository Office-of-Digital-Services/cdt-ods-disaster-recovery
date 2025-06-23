# Diagnostic settings for the PostgreSQL Flexible Server
resource "azurerm_monitor_diagnostic_setting" "db" {
  name                       = "${var.diagnostic_setting_prefix}-db"
  target_resource_id         = azurerm_postgresql_flexible_server.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category_group = "allLogs"
  }

  enabled_log {
    category_group = "audit"
  }
}
