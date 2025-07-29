output "log_analytics_workspace_id" {
  description = "The unique ID of the Log Analytics Workspace, needed by other modules for diagnostic settings."
  value       = azurerm_log_analytics_workspace.main.id
}

output "application_insights_id" {
  description = "The ID of the Application Insights resource."
  value       = azurerm_application_insights.main.id
}

output "application_insights_connection_string" {
  description = "The connection string for applications to connect to Application Insights."
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "application_insights_instrumentation_key" {
  description = "The instrumentation key for applications to send telemetry to Application Insights."
  value       = azurerm_application_insights.main.instrumentation_key
}

output "action_group_id" {
  description = "The ID of the monitor action group."
  value       = azurerm_monitor_action_group.eng_email.id
}
