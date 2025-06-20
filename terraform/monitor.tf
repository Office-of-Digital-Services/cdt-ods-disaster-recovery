locals {
  diagnostic_setting_name_prefix = lower("MDS-CDT-PUB-VIP-DDRC-${local.env_letter}")
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "CDT-OET-PUB-DDRC-${local.env_letter}-001"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_application_insights" "main" {
  name                = "AI-CDT-PUB-VIP-DDRC-${local.env_letter}-001"
  application_type    = "web"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  sampling_percentage = 0
  workspace_id        = azurerm_log_analytics_workspace.main.id

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_monitor_action_group" "eng_email" {
  name                = "ddrc-notify Slack channel email"
  resource_group_name = data.azurerm_resource_group.main.name
  short_name          = "slack-notify"

  email_receiver {
    name          = "ddrc engineering team"
    email_address = var.SLACK_NOTIFY_EMAIL
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
# Diagnostic settings for the Application Gateway
resource "azurerm_monitor_diagnostic_setting" "gateway" {
  name                       = "${local.diagnostic_setting_name_prefix}-gateway"
  target_resource_id         = azurerm_application_gateway.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category_group = "allLogs"
  }

  enabled_log {
    category_group = "AllMetrics"
  }
}

# Diagnostic settings for the PostgreSQL Flexible Server
resource "azurerm_monitor_diagnostic_setting" "db" {
  name                       = "${local.diagnostic_setting_name_prefix}-db"
  target_resource_id         = azurerm_postgresql_flexible_server.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category_group = "allLogs"
  }

  enabled_log {
    category_group = "AllMetrics"
  }
}

# Diagnostic settings for the Key Vault
resource "azurerm_monitor_diagnostic_setting" "keyvault" {
  name                       = "${local.diagnostic_setting_name_prefix}-kv"
  target_resource_id         = azurerm_key_vault.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category_group = "allLogs"
  }

  enabled_log {
    category_group = "AllMetrics"
  }
}

# Diagnostic settings for the Gateway NSG
resource "azurerm_monitor_diagnostic_setting" "nsg_gateway" {
  name                       = "${local.diagnostic_setting_name_prefix}-nsg-gateway"
  target_resource_id         = azurerm_network_security_group.gateway.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category_group = "allLogs"
  }

  enabled_log {
    category_group = "AllMetrics"
  }
}

# Diagnostic settings for the Public Subnet NSG
resource "azurerm_monitor_diagnostic_setting" "nsg_public" {
  name                       = "${local.diagnostic_setting_name_prefix}-nsg-public"
  target_resource_id         = azurerm_network_security_group.public.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category_group = "allLogs"
  }

  enabled_log {
    category_group = "AllMetrics"
  }
}

# Diagnostic settings for the Worker Subnet NSG
resource "azurerm_monitor_diagnostic_setting" "nsg_worker" {
  name                       = "${local.diagnostic_setting_name_prefix}-nsg-worker"
  target_resource_id         = azurerm_network_security_group.worker.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category_group = "allLogs"
  }

  enabled_log {
    category_group = "AllMetrics"
  }
}
