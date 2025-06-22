# This module creates the shared monitoring and alerting infrastructure.

resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_workspace_name
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

resource "azurerm_monitor_action_group" "eng_email" {
  name                = var.action_group_name
  resource_group_name = var.resource_group_name
  short_name          = var.action_group_short_name

  email_receiver {
    name          = "engineering team"
    email_address = var.notification_email_address
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
