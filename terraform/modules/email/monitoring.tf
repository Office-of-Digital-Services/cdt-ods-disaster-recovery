# Diagnostic settings for Communication Services
resource "azurerm_monitor_diagnostic_setting" "email" {
  name                       = "${var.diagnostic_setting_prefix}-email"
  target_resource_id         = azurerm_communication_service.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "EmailSendMailOperational"
  }

  enabled_log {
    category = "EmailStatusUpdateOperational"
  }

  enabled_log {
    category = "EmailUserEngagementOperational"
  }

  enabled_metric {
    category = "Traffic"
  }
}
