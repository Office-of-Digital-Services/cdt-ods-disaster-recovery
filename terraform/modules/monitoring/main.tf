# This module creates the shared monitoring and alerting infrastructure.

resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_workspace_name
  location            = var.location
  resource_group_name = var.resource_group_name

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_monitor_workspace" "main" {
  name                = var.monitor_workspace_name
  location            = var.location
  resource_group_name = var.resource_group_name

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_application_insights" "main" {
  name                = var.application_insights_name
  application_type    = "web"
  location            = var.location
  resource_group_name = var.resource_group_name
  sampling_percentage = 0
  workspace_id        = azurerm_log_analytics_workspace.main.id

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_monitor_action_group" "main" {
  name                = var.action_group_name
  resource_group_name = var.resource_group_name
  short_name          = var.action_group_short_name

  email_receiver {
    name          = "engineering team"
    email_address = var.notification_email_address
  }

  webhook_receiver {
    name        = "funcapp-webhook"
    service_uri = "https://${var.functions_app_hostname}/api/alert_to_slack?code=${var.functions_app_hostkey}"
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
